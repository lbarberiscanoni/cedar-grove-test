"""
review.py — Claude review + orchestration, with a server-friendly core.

Layering (so a future email/HTTP trigger can wrap the logic without the CLI):

    review_bytes(docx_bytes)   -> ReviewResult        # pure, no filesystem
    review_document(doc)       -> ReviewResult         # operate on an open Document
    review(path, out_dir=...)  -> (paths, ReviewResult)# filesystem/CLI convenience

Nothing here touches pandoc or LibreOffice — the pipeline has no runtime dependency
on an office stack, so it deploys to a plain Python server. Those tools are only
used by the test suite to validate output.

Privacy: this module never logs contract text. Logs carry counts and paragraph
indices only. Enable Zero Data Retention on the Anthropic workspace before sending
real client documents.
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

import anthropic
from docx import Document

from redline_engine import (
    DEFAULT_AUTHOR,
    Edit,
    FlaggedEdit,
    apply_edits,
    extract_paragraphs,
    numbered_text,
)

logger = logging.getLogger("cedar_grove.review")

# --- Configuration (all overridable via environment, for per-deploy tuning) ---

MODEL = os.getenv("CEDAR_GROVE_MODEL", "claude-opus-4-7")
MAX_TOKENS = int(os.getenv("CEDAR_GROVE_MAX_TOKENS", "8000"))
API_TIMEOUT = float(os.getenv("CEDAR_GROVE_API_TIMEOUT", "600"))       # seconds
API_MAX_RETRIES = int(os.getenv("CEDAR_GROVE_API_MAX_RETRIES", "4"))
REDLINE_AUTHOR = os.getenv("CEDAR_GROVE_REDLINE_AUTHOR", DEFAULT_AUTHOR)

# Skill/playbook directory. Override CEDAR_GROVE_SKILL_DIR if the server mounts the
# playbook elsewhere (e.g. a secret/volume).
SKILL_DIR = Path(os.getenv("CEDAR_GROVE_SKILL_DIR",
                           str(Path(__file__).resolve().parent / "skill")))

# Where outputs go when --out-dir isn't given: the directory the code lives in.
# Override with CEDAR_GROVE_OUTPUT_DIR or the -o flag.
DEFAULT_OUTPUT_DIR = Path(os.getenv("CEDAR_GROVE_OUTPUT_DIR",
                                    str(Path(__file__).resolve().parent)))


@dataclass
class ReviewResult:
    """Everything the caller needs; no filesystem assumptions."""
    redlined_bytes: bytes
    flagged: list[dict] = field(default_factory=list)
    num_edits_proposed: int = 0
    num_applied: int = 0

    @property
    def num_flagged(self) -> int:
        return len(self.flagged)

    def flagged_json(self) -> str:
        return json.dumps(self.flagged, indent=2, ensure_ascii=False)


@lru_cache(maxsize=1)
def _load_skill_and_playbook() -> tuple[str, str]:
    """Read skill + playbook once per process (they are constant across contracts)."""
    skill = (SKILL_DIR / "SKILL.md").read_text()
    playbook = (SKILL_DIR / "PLAYBOOK.md").read_text()
    return skill, playbook


# --- Response parsing ---------------------------------------------------------

_FENCE_RE = re.compile(r"^```(?:\w+)?\s*(.*?)\s*```$", re.DOTALL)


def strip_fences(s: str) -> str:
    """Strip a single ```lang … ``` wrapper if present (the model is told not to use
    fences, but cheap defense against drift)."""
    s = s.strip()
    m = _FENCE_RE.match(s)
    return m.group(1).strip() if m else s


def parse_edits(raw: str) -> list[Edit]:
    data = json.loads(strip_fences(raw))
    return [
        Edit(
            para=int(e["para"]),
            type=e.get("type", "replace"),
            find=e.get("find", ""),
            replace=e.get("replace", ""),
            severity=e.get("severity", ""),
            comment=e.get("comment", ""),
        )
        for e in data.get("edits", [])
    ]


# --- API ----------------------------------------------------------------------


def build_client() -> anthropic.Anthropic:
    """Construct an Anthropic client with server-appropriate timeout/retry.

    Reads ANTHROPIC_API_KEY from the environment (SDK default). A custom
    ANTHROPIC_BASE_URL is honored automatically by the SDK for enterprise gateways.
    """
    return anthropic.Anthropic(timeout=API_TIMEOUT, max_retries=API_MAX_RETRIES)


def call_claude(numbered_contract: str, skill: str, playbook: str,
                client: Optional[anthropic.Anthropic] = None) -> list[Edit]:
    """Call Claude and return parsed edits.

    Skill + playbook live in the system prompt; the playbook is cached with a 1-hour
    TTL because it is identical across every contract and the default ephemeral TTL
    is only 5 minutes.
    """
    if client is None:
        client = build_client()

    system = [
        {"type": "text", "text": skill},
        {
            "type": "text",
            "text": playbook,
            "cache_control": {"type": "ephemeral", "ttl": "1h"},
        },
    ]

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{
            "role": "user",
            "content": (
                "Review the following contract against the playbook. "
                "Respond with the JSON edits object only.\n\n" + numbered_contract
            ),
        }],
    )
    usage = getattr(response, "usage", None)
    if usage is not None:
        logger.info(
            "claude usage: in=%s out=%s cache_read=%s cache_write=%s",
            getattr(usage, "input_tokens", "?"),
            getattr(usage, "output_tokens", "?"),
            getattr(usage, "cache_read_input_tokens", "?"),
            getattr(usage, "cache_creation_input_tokens", "?"),
        )
    return parse_edits(response.content[0].text)


# --- Core (server entry points) -----------------------------------------------


def review_document(doc, client: Optional[anthropic.Anthropic] = None,
                    author: str = REDLINE_AUTHOR) -> ReviewResult:
    """Review an open python-docx Document in place and return a ReviewResult.

    The Document is mutated (tracked changes applied). Pure aside from the Claude
    call — no filesystem access.
    """
    paragraphs = extract_paragraphs(doc)
    logger.info("extracted %d paragraphs", len(paragraphs))

    skill, playbook = _load_skill_and_playbook()
    edits = call_claude(numbered_text(paragraphs), skill, playbook, client=client)
    logger.info("model proposed %d edits", len(edits))

    flagged = apply_edits(doc, paragraphs, edits, author=author)
    applied = len(edits) - len(flagged)
    logger.info("applied %d edits, flagged %d", applied, len(flagged))

    buf = io.BytesIO()
    doc.save(buf)
    redlined = buf.getvalue()

    # Round-trip validity: malformed XML would raise here.
    Document(io.BytesIO(redlined))

    return ReviewResult(
        redlined_bytes=redlined,
        flagged=[f.to_dict() if isinstance(f, FlaggedEdit) else f for f in flagged],
        num_edits_proposed=len(edits),
        num_applied=applied,
    )


def review_bytes(docx_bytes: bytes,
                 client: Optional[anthropic.Anthropic] = None,
                 author: str = REDLINE_AUTHOR) -> ReviewResult:
    """Review a .docx given as bytes; return redlined bytes + flagged edits.

    This is the entry point a future email/HTTP trigger should call: hand it the
    attachment bytes, store `result.redlined_bytes` and `result.flagged`.
    """
    doc = Document(io.BytesIO(docx_bytes))
    return review_document(doc, client=client, author=author)


# --- Filesystem / CLI convenience ---------------------------------------------


def review(input_path: str, out_dir: Optional[str] = None,
           client: Optional[anthropic.Anthropic] = None,
           author: str = REDLINE_AUTHOR) -> tuple[Path, Path, ReviewResult]:
    """Path-based wrapper. Returns (redlined_docx_path, flagged_json_path, result)."""
    in_path = Path(input_path)
    if not in_path.exists():
        raise FileNotFoundError(in_path)
    out_base = Path(out_dir) if out_dir else DEFAULT_OUTPUT_DIR
    out_base.mkdir(parents=True, exist_ok=True)
    out_docx = out_base / f"{in_path.stem}.redlined.docx"
    out_json = out_base / f"{in_path.stem}.flagged.json"

    result = review_bytes(in_path.read_bytes(), client=client, author=author)

    out_docx.write_bytes(result.redlined_bytes)
    out_json.write_text(result.flagged_json())
    return out_docx, out_json, result


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Review a .docx contract against the firm playbook.")
    parser.add_argument("input", help="Path to the input .docx contract")
    parser.add_argument("-o", "--out-dir", default=None,
                        help="Directory for outputs (default: the project directory "
                             "where review.py lives)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Log progress (counts only; never contract text)")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is not set in the environment.", file=sys.stderr)
        return 1

    try:
        out_docx, out_json, result = review(args.input, out_dir=args.out_dir)
    except FileNotFoundError as e:
        print(f"ERROR: input file not found: {e}", file=sys.stderr)
        return 1

    print(f"Redlined:  {out_docx}")
    print(f"Flagged:   {out_json}  "
          f"({result.num_applied} applied, {result.num_flagged} flagged for human review)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
