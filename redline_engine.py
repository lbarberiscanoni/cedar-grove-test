"""
redline_engine.py — DOCX extraction, validation gate, and tracked-changes apply.

Pure DOCX / OOXML operations. No Claude API in here — see review.py for that, so
the email trigger can later wrap the engine without dragging the API in.

Handles documents that ALREADY contain tracked changes (the normal case: a
counterparty redline arrives with their <w:ins>/<w:del> in place). The model
reviews the *current visible* text (counterparty insertions included, their
deletions excluded). When our edit lands inside text the counterparty inserted, we
layer our change as a tracked change nested inside theirs (split their <w:ins>,
nest a <w:del>, add our own <w:ins>) so accept/reject behave correctly in Word.
Edits that straddle a tracked-change boundary are ambiguous and are flagged for a
human rather than guessed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"


def W(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def XML(tag: str) -> str:
    return f"{{{XML_NS}}}{tag}"


# Default per the apply-redlines skill convention. Override via apply_edits(author=)
# or the CEDAR_GROVE_REDLINE_AUTHOR env var (see review.py).
DEFAULT_AUTHOR = "Michael Ohta"


# --- Data model ---------------------------------------------------------------


@dataclass
class RunInfo:
    """A run whose text contributes to the visible paragraph text."""
    text: str
    rPr_xml: Optional[bytes]      # serialized <w:rPr> or None
    element: etree._Element       # the original <w:r>


@dataclass
class Target:
    """A contiguous, independently-editable region of a paragraph.

    Two kinds:
      - "editable": a maximal run of direct <w:r> children of <w:p> with no
        tracked-change element between them. Edits here become plain
        <w:del>/<w:ins> siblings.
      - "ins": a single counterparty <w:ins> element. Its inner runs are visible
        text. Edits here are layered: the <w:ins> is split and our <w:del>/<w:ins>
        are nested/placed so Word accept/reject stays correct.

    `anchor_elements` are the parent's children we replace on splice (for
    "editable", the direct <w:r>s; for "ins", the single <w:ins> element).
    """
    kind: str
    runs: list[RunInfo]
    v_start: int
    anchor_elements: list[etree._Element]
    parent: etree._Element
    ins_author: Optional[str] = None
    ins_date: Optional[str] = None
    # For "ins" targets: True iff the <w:ins> contains only runs (safe to rebuild).
    # A counterparty <w:ins> with other children (e.g. a nested <w:del>) would lose
    # that content on rebuild, so edits touching it are flagged instead.
    ins_simple: bool = True

    @property
    def local_text(self) -> str:
        return "".join(r.text for r in self.runs)

    @property
    def v_end(self) -> int:
        return self.v_start + len(self.local_text)


@dataclass
class ParagraphInfo:
    """A <w:p> in document order (including paragraphs in tables)."""
    index: int
    element: etree._Element
    targets: list[Target] = field(default_factory=list)
    visible_text: str = ""

    @property
    def text(self) -> str:
        # The current visible text: counterparty insertions included, deletions
        # excluded. This is what the model reviews and what `find` matches against.
        return self.visible_text


@dataclass
class Edit:
    para: int
    type: str = "replace"          # "replace" or "delete"
    find: str = ""
    replace: str = ""
    severity: str = ""
    comment: str = ""

    @property
    def is_delete(self) -> bool:
        return self.type == "delete" or not self.replace

    def to_dict(self) -> dict:
        return {
            "para": self.para,
            "type": self.type,
            "find": self.find,
            "replace": self.replace,
            "severity": self.severity,
            "comment": self.comment,
        }


@dataclass
class FlaggedEdit:
    edit: dict
    reason: str

    def to_dict(self) -> dict:
        return {"edit": self.edit, "reason": self.reason}


# --- Extraction ---------------------------------------------------------------


def _run_text(r: etree._Element) -> str:
    """Concatenate the <w:t> text of a <w:r> (tabs/breaks contribute nothing)."""
    return "".join(c.text or "" for c in r if c.tag == W("t"))


def _ins_runs(ins: etree._Element) -> list[RunInfo]:
    """Visible runs inside a <w:ins>: its direct <w:r> children.

    Any <w:del> nested inside the ins is counterparty-inserted-then-deleted text:
    not visible, skipped.
    """
    runs: list[RunInfo] = []
    for r in ins:
        if r.tag != W("r"):
            continue
        rPr = r.find(W("rPr"))
        rPr_xml = etree.tostring(rPr) if rPr is not None else None
        runs.append(RunInfo(text=_run_text(r), rPr_xml=rPr_xml, element=r))
    return runs


def _build_targets(p: etree._Element) -> tuple[list[Target], str]:
    """Walk a paragraph's children, producing editable/ins targets and visible text.

    Children that are neither runs nor tracked-change elements (pPr, bookmarks,
    proofErr, …) are transparent: they do not contribute text and do not break an
    editable zone.
    """
    targets: list[Target] = []
    visible_parts: list[str] = []
    v_pos = 0

    # Accumulator for the current editable zone.
    zone_runs: list[RunInfo] = []
    zone_elems: list[etree._Element] = []
    zone_start = 0

    def flush_zone():
        nonlocal zone_runs, zone_elems, zone_start
        if zone_runs:
            targets.append(Target(
                kind="editable", runs=zone_runs, v_start=zone_start,
                anchor_elements=zone_elems, parent=p,
            ))
        zone_runs = []
        zone_elems = []

    for child in p:
        tag = child.tag
        if tag == W("r"):
            rPr = child.find(W("rPr"))
            rPr_xml = etree.tostring(rPr) if rPr is not None else None
            text = _run_text(child)
            if not zone_runs:
                zone_start = v_pos
            zone_runs.append(RunInfo(text=text, rPr_xml=rPr_xml, element=child))
            zone_elems.append(child)
            visible_parts.append(text)
            v_pos += len(text)
        elif tag == W("ins"):
            flush_zone()
            runs = _ins_runs(child)
            text = "".join(r.text for r in runs)
            # Simple iff every child is a run (or rPr); otherwise rebuilding the ins
            # would drop nested content (e.g. an inserted-then-deleted <w:del>).
            simple = all(c.tag in (W("r"), W("rPr")) for c in child)
            targets.append(Target(
                kind="ins", runs=runs, v_start=v_pos,
                anchor_elements=[child], parent=p,
                ins_author=child.get(W("author")),
                ins_date=child.get(W("date")),
                ins_simple=simple,
            ))
            visible_parts.append(text)
            v_pos += len(text)
        elif tag == W("del"):
            # Counterparty deletion: not visible. Breaks the editable zone.
            flush_zone()
        # else: transparent child — leave zone intact.

    flush_zone()
    return targets, "".join(visible_parts)


def extract_paragraphs(doc) -> list[ParagraphInfo]:
    """Every <w:p> in document order, including inside tables.

    The numbered text the model sees AND the apply step both walk this exact list,
    so indices never drift on schedules / signature blocks. Accepts a python-docx
    Document or anything exposing `.element.body`.
    """
    body = doc.element.body
    paragraphs: list[ParagraphInfo] = []
    for idx, p in enumerate(body.iter(W("p"))):
        targets, visible = _build_targets(p)
        paragraphs.append(ParagraphInfo(
            index=idx, element=p, targets=targets, visible_text=visible,
        ))
    return paragraphs


def numbered_text(paragraphs: list[ParagraphInfo]) -> str:
    """Produce the `[¶N] text` representation the model sees (current visible text)."""
    return "\n".join(f"[¶{p.index}] {p.text}" for p in paragraphs)


# --- Normalization & matching -------------------------------------------------


# 1:1 character substitutions for matching tolerance.
_CHAR_MAP = {
    "“": '"', "”": '"',
    "‘": "'", "’": "'",
    "–": "-", "—": "-",
    " ": " ",  # non-breaking space -> regular space
}


def normalize_with_map(s: str) -> tuple[str, list[int]]:
    """Return (normalized, orig_index_map).

    `orig_index_map[i]` is the start index in `s` of the i-th normalized char.
    A trailing entry equal to `len(s)` lets callers read the original end offset.
    Consecutive spaces collapse to one (kept space maps to the first original
    space in the run).
    """
    out: list[str] = []
    index_map: list[int] = []
    prev_was_space = False
    for i, ch in enumerate(s):
        nch = _CHAR_MAP.get(ch, ch)
        if nch == " ":
            if prev_was_space:
                continue
            prev_was_space = True
        else:
            prev_was_space = False
        out.append(nch)
        index_map.append(i)
    index_map.append(len(s))
    return "".join(out), index_map


def find_unique_match(haystack: str, needle: str) -> Optional[tuple[int, int]]:
    """(orig_start, orig_end) for the unique match of `needle`, or None if the
    match count is not exactly one. Indices are in the ORIGINAL `haystack`."""
    n_hay, hay_map = normalize_with_map(haystack)
    n_needle, _ = normalize_with_map(needle)
    if not n_needle:
        return None
    matches = [m.start() for m in re.finditer(re.escape(n_needle), n_hay)]
    if len(matches) != 1:
        return None
    n_start = matches[0]
    n_end = n_start + len(n_needle)
    return hay_map[n_start], hay_map[n_end]


def _count_matches(haystack: str, needle: str) -> int:
    n_hay, _ = normalize_with_map(haystack)
    n_needle, _ = normalize_with_map(needle)
    if not n_needle:
        return 0
    return len(re.findall(re.escape(n_needle), n_hay))


# --- Element builders ---------------------------------------------------------


def _make_t(text: str, use_del_text: bool) -> etree._Element:
    tag = "delText" if use_del_text else "t"
    t = etree.Element(W(tag))
    t.text = text
    if text and text != text.strip():
        t.set(XML("space"), "preserve")
    return t


def _make_r(text: str, rPr_xml: Optional[bytes], use_del_text: bool) -> etree._Element:
    r = etree.Element(W("r"))
    if rPr_xml:
        r.append(etree.fromstring(rPr_xml))  # fresh node per run
    r.append(_make_t(text, use_del_text))
    return r


def _make_wrapper(tag: str, change_id: int, author: str, date_str: str,
                  children: list[etree._Element]) -> etree._Element:
    """Build a <w:ins> or <w:del> with id/author/date and the given children."""
    elem = etree.Element(W(tag))
    elem.set(W("id"), str(change_id))
    elem.set(W("author"), author)
    elem.set(W("date"), date_str)
    for c in children:
        elem.append(c)
    return elem


# --- Single-pass rebuild ------------------------------------------------------


# A fragment of the rebuilt text region, in document order.
#   ("keep", [(text, rPr), ...])  — unchanged text (split at run boundaries)
#   ("del",  [(text, rPr), ...])  — text we are deleting
#   ("ins",  text, rPr)           — text we are inserting
Fragment = tuple


def _slices_for_range(units: list[tuple[int, int, str, Optional[bytes]]],
                      start: int, end: int) -> list[tuple[str, Optional[bytes]]]:
    """Split [start,end) of the local text into (text, rPr) pieces at unit
    (formatting) boundaries, so intra-run formatting survives on kept/deleted text."""
    out: list[tuple[str, Optional[bytes]]] = []
    for u_start, u_end, u_text, u_rPr in units:
        if u_end <= start or u_start >= end:
            continue
        ov_start = max(start, u_start)
        ov_end = min(end, u_end)
        if ov_end <= ov_start:
            continue
        piece = u_text[ov_start - u_start: ov_end - u_start]
        if piece:
            out.append((piece, u_rPr))
    return out


def _rPr_at(units: list[tuple[int, int, str, Optional[bytes]]], pos: int) -> Optional[bytes]:
    if not units:
        return None
    for u_start, u_end, _, u_rPr in units:
        if u_start <= pos < u_end:
            return u_rPr
    return units[-1][3]


def _rebuild_fragments(runs: list[RunInfo],
                       ops: list[tuple[int, int, Optional[str]]]) -> list[Fragment]:
    """Walk the local text once, emitting keep/del/ins fragments in order.

    `ops` is the already-sorted, non-overlapping list of (start, end, insert_text)
    in local coordinates. `insert_text` is the text to insert after deleting
    [start, end) (None/"" => delete-only). A single edit that straddles several
    targets contributes one op here per target it touches, with `insert_text` set on
    only one of them. No op ever sees a half-modified region.
    """
    units: list[tuple[int, int, str, Optional[bytes]]] = []
    pos = 0
    for r in runs:
        n = len(r.text)
        if n > 0:
            units.append((pos, pos + n, r.text, r.rPr_xml))
            pos += n
    full_len = pos

    fragments: list[Fragment] = []
    cursor = 0
    for span_start, span_end, insert_text in ops:
        if cursor < span_start:
            fragments.append(("keep", _slices_for_range(units, cursor, span_start)))
        del_slices = _slices_for_range(units, span_start, span_end)
        if del_slices:
            fragments.append(("del", del_slices))
        if insert_text:
            fragments.append(("ins", insert_text, _rPr_at(units, span_start)))
        cursor = span_end
    if cursor < full_len:
        fragments.append(("keep", _slices_for_range(units, cursor, full_len)))
    return fragments


# --- Fragment emitters (per target kind) --------------------------------------


def _emit_editable(fragments: list[Fragment], id_counter: list[int],
                   author: str, date_str: str) -> list[etree._Element]:
    """Editable zone: keep -> bare runs, del -> <w:del>, ins -> <w:ins>."""
    out: list[etree._Element] = []
    for frag in fragments:
        if frag[0] == "keep":
            for text, rPr in frag[1]:
                out.append(_make_r(text, rPr, use_del_text=False))
        elif frag[0] == "del":
            runs = [_make_r(t, rPr, use_del_text=True) for t, rPr in frag[1]]
            cid = id_counter[0]; id_counter[0] += 1
            out.append(_make_wrapper("del", cid, author, date_str, runs))
        elif frag[0] == "ins":
            _, text, rPr = frag
            cid = id_counter[0]; id_counter[0] += 1
            out.append(_make_wrapper("ins", cid, author, date_str,
                                     [_make_r(text, rPr, use_del_text=False)]))
    return out


def _emit_inside_ins(fragments: list[Fragment], id_counter: list[int],
                     author: str, date_str: str,
                     cp_author: Optional[str], cp_date: Optional[str]) -> list[etree._Element]:
    """Inside a counterparty <w:ins>: split it around our change.

    keep -> <w:ins cp> kept runs (still counterparty's insertion)
    del  -> <w:ins cp><w:del us> runs </w:del></w:ins> (their insertion, our deletion)
    ins  -> <w:ins us> our run (our replacement)
    """
    cp_author = cp_author or "Counterparty"
    cp_date = cp_date or date_str
    out: list[etree._Element] = []
    for frag in fragments:
        if frag[0] == "keep":
            runs = [_make_r(t, rPr, use_del_text=False) for t, rPr in frag[1]]
            if runs:
                cid = id_counter[0]; id_counter[0] += 1
                out.append(_make_wrapper("ins", cid, cp_author, cp_date, runs))
        elif frag[0] == "del":
            runs = [_make_r(t, rPr, use_del_text=True) for t, rPr in frag[1]]
            del_id = id_counter[0]; id_counter[0] += 1
            del_el = _make_wrapper("del", del_id, author, date_str, runs)
            ins_id = id_counter[0]; id_counter[0] += 1
            out.append(_make_wrapper("ins", ins_id, cp_author, cp_date, [del_el]))
        elif frag[0] == "ins":
            _, text, rPr = frag
            cid = id_counter[0]; id_counter[0] += 1
            out.append(_make_wrapper("ins", cid, author, date_str,
                                     [_make_r(text, rPr, use_del_text=False)]))
    return out


def _splice(target: Target, new_elements: list[etree._Element]) -> None:
    """Replace the target's anchor elements with new_elements, in place."""
    parent = target.parent
    children = list(parent)
    first_idx = children.index(target.anchor_elements[0])
    for el in target.anchor_elements:
        parent.remove(el)
    for offset, ne in enumerate(new_elements):
        parent.insert(first_idx + offset, ne)


# --- Apply --------------------------------------------------------------------


def _apply_to_paragraph(p_info: ParagraphInfo, edits: list[Edit],
                        id_counter: list[int], author: str,
                        date_str: str) -> list[FlaggedEdit]:
    flagged: list[FlaggedEdit] = []
    visible = p_info.visible_text

    # Map each visible char to the index of its owning target (targets are
    # contiguous & ordered). -1 means no target (cannot happen for visible chars).
    char_target: list[int] = [-1] * len(visible)
    for ti, t in enumerate(p_info.targets):
        for i in range(t.v_start, t.v_end):
            char_target[i] = ti

    # Match each edit against the original visible text and record its span.
    matched: list[tuple[int, int, Edit]] = []
    for e in edits:
        match = find_unique_match(visible, e.find)
        if match is None:
            count = _count_matches(visible, e.find)
            reason = ("find string not found in paragraph" if count == 0
                      else f"find string has {count} matches in paragraph (must be unique)")
            flagged.append(FlaggedEdit(edit=e.to_dict(), reason=reason))
            continue
        matched.append((match[0], match[1], e))

    # Reject overlapping edits at the paragraph level (so the per-target ops we derive
    # below are inherently non-overlapping). Earlier-starting edit wins.
    matched.sort(key=lambda m: (m[0], m[1]))
    accepted_edits: list[tuple[int, int, Edit]] = []
    last_end = -1
    for start, end, e in matched:
        if start < last_end:
            flagged.append(FlaggedEdit(
                edit=e.to_dict(),
                reason="edit span overlaps another edit in the same paragraph",
            ))
            continue
        accepted_edits.append((start, end, e))
        last_end = end

    # Decompose each accepted edit into one op per target its span touches. An edit
    # that straddles a tracked-change boundary thus layers across targets instead of
    # being flagged. The replacement text attaches to the target containing `start`.
    # ops_by_target: target index -> list of (local_start, local_end, insert_text|None)
    ops_by_target: dict[int, list[tuple[int, int, Optional[str]]]] = {}
    for start, end, e in accepted_edits:
        covered = sorted({char_target[i] for i in range(start, end)})
        # Guard: refuse to layer into a counterparty <w:ins> with nested content.
        if any(p_info.targets[ti].kind == "ins" and not p_info.targets[ti].ins_simple
               for ti in covered):
            flagged.append(FlaggedEdit(
                edit=e.to_dict(),
                reason="edit touches a complex existing insertion; needs human review",
            ))
            continue
        first_ti = char_target[start]
        insert_text = "" if e.is_delete else e.replace
        for ti in covered:
            t = p_info.targets[ti]
            os_ = max(start, t.v_start)
            oe_ = min(end, t.v_end)
            if oe_ <= os_:
                continue
            ins_here = insert_text if ti == first_ti else None
            ops_by_target.setdefault(ti, []).append(
                (os_ - t.v_start, oe_ - t.v_start, ins_here))

    # Rebuild each touched target once, in a single pass over its original text.
    for ti, ops in ops_by_target.items():
        target = p_info.targets[ti]
        ops.sort(key=lambda o: (o[0], o[1]))
        fragments = _rebuild_fragments(target.runs, ops)
        if target.kind == "editable":
            new_elements = _emit_editable(fragments, id_counter, author, date_str)
        else:  # "ins"
            new_elements = _emit_inside_ins(
                fragments, id_counter, author, date_str,
                target.ins_author, target.ins_date,
            )
        _splice(target, new_elements)

    return flagged


def apply_edits(doc, paragraphs: list[ParagraphInfo], edits: list[Edit],
                author: str = DEFAULT_AUTHOR,
                now: Optional[datetime] = None) -> list[FlaggedEdit]:
    """Apply edits in-place. Returns the edits that could not be applied (with a
    reason for each)."""
    flagged: list[FlaggedEdit] = []

    by_para: dict[int, list[Edit]] = {}
    for e in edits:
        if e.para < 0 or e.para >= len(paragraphs):
            flagged.append(FlaggedEdit(
                edit=e.to_dict(),
                reason=f"paragraph index {e.para} out of range (0..{len(paragraphs)-1})",
            ))
            continue
        by_para.setdefault(e.para, []).append(e)

    if now is None:
        now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    id_counter = [_next_change_id(doc)]

    for para_idx, para_edits in by_para.items():
        flagged.extend(_apply_to_paragraph(
            paragraphs[para_idx], para_edits, id_counter, author, date_str,
        ))

    return flagged


def _next_change_id(doc) -> int:
    """Pick an ID above any existing w:id on tracked-change elements, so we never
    collide with a counterparty's existing <w:ins>/<w:del> ids."""
    max_id = 0
    for tag in ("ins", "del"):
        for el in doc.element.body.iter(W(tag)):
            v = el.get(W("id"))
            if v and v.isdigit():
                max_id = max(max_id, int(v))
    return max_id + 1
