# Cedar Grove Contract Redline Pipeline (MVP)

Reviews a `.docx` contract against a firm playbook using the Claude API and produces
a Word doc with **native tracked changes** (insertions and deletions a lawyer
accepts or rejects in Word). Runs as a CLI locally and as a stateless, bytes-in /
bytes-out function on a server.

```
python review.py contract.docx
  → contract.redlined.docx    # tracked changes, open in Word
  → contract.flagged.json     # edits that couldn't be applied cleanly
```

## Setup

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...
```

The real Juicebox ESA playbook lives in `skill/PLAYBOOK.md`; the review skill (the
JSON edit contract) is in `skill/SKILL.md`.

## Web UI

[app.py](app.py) is a small Flask app: upload a `.docx`, get a results page with a
summary, the flagged edits, and a download for the redlined `.docx`.

```
ANTHROPIC_API_KEY=sk-... python app.py            # dev server on :8000
# production-style:
ANTHROPIC_API_KEY=sk-... gunicorn --bind 0.0.0.0:8000 --timeout 120 --workers 1 app:app
```

Open <http://localhost:8000>. Routes: `GET /` (form), `POST /review` (process →
results page with the redlined docx embedded for client-side download), `GET /healthz`.
The app holds **no server-side state** — the redlined file is embedded in the results
page and downloaded via a Blob in the browser, so a download can't 404 after a worker
restart, redeploy, or multi-instance routing.

## Deploy to Render

1. **Push to Git.** This repo isn't initialized yet — `git init`, commit, and push to
   GitHub/GitLab (Render deploys from a connected repo).
2. **Create the service.** In Render: **New + → Blueprint**, point it at the repo. It
   reads [render.yaml](render.yaml) (build = `pip install -r requirements.txt`, start =
   `gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 --max-requests 100 app:app`,
   health check `/healthz`, Python pinned via `.python-version` / `PYTHON_VERSION`).
3. **Set the secret.** Add `ANTHROPIC_API_KEY` in the dashboard (marked `sync: false`
   in the blueprint so it isn't stored in Git). Optionally set `APP_PASSWORD` to gate
   the whole site behind HTTP Basic Auth — leave it unset for open access.
4. **Deploy**, then hit `/healthz` (should be `ok`) and the root URL.

Why `--timeout 120`: a review takes ~26s and gunicorn's default 30s worker timeout
would kill longer ones. The **free tier cold-starts** (~30–60s) before that ~26s
review, so the first request after idle is slow — use the **starter** plan for
responsiveness.

### Programmatic API (`POST /api/review`) — for the email/automation trigger

For automated callers (e.g. the email pipeline), use the JSON API instead of the HTML
form. Send the `.docx` as the raw request body (or a multipart `file` field) and get
back the redlined file (base64) plus the flagged edits:

```bash
curl -X POST \
  -H "Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document" \
  -H "X-Filename: contract.docx" \
  --data-binary @contract.docx \
  https://<your-app>.onrender.com/api/review
```

Response:

```json
{
  "filename": "contract.redlined.docx",
  "applied": 15,
  "flagged_count": 0,
  "flagged": [ { "edit": { "para": 21, ... }, "reason": "..." } ],
  "redlined_docx_base64": "UEsDBBQ..."
}
```

What an email worker does with it (Python):

```python
import base64, requests

resp = requests.post(
    "https://<your-app>.onrender.com/api/review",
    data=open("contract.docx", "rb").read(),
    headers={"X-Filename": "contract.docx"},
    timeout=180,
)
out = resp.json()
with open(out["filename"], "wb") as f:
    f.write(base64.b64decode(out["redlined_docx_base64"]))
# ...reply to the email with out["filename"]; route out["flagged"] to a human queue.
```

If `APP_PASSWORD` is set, add `auth=("api", "<password>")` (Basic auth). Errors return
`{"error": "..."}` with a 4xx/5xx status. Note: the email trigger could also skip HTTP
entirely and call `review_bytes()` in-process — the API exists for an out-of-process
or cross-service caller.

### Server core (for the future email trigger)

The review logic is filesystem-free and importable, so a trigger (email poll, queue
worker) wraps it without the CLI or the web app:

```python
from review import review_bytes

result = review_bytes(docx_bytes)          # bytes in
result.redlined_bytes                       # → redlined .docx (bytes)
result.flagged                              # → list of edits needing human review
result.num_applied, result.num_flagged
```

`review_bytes` is **stateless and idempotent** — each call builds its own `Document`,
so it is safe to run concurrently per request.

**No office stack required at runtime.** The pipeline depends only on
`flask` / `gunicorn` / `python-docx` / `lxml` / `anthropic` — *not* on pandoc or
LibreOffice. Those are used only by the test suite to validate output, so the
production image stays slim.

### Configuration (environment variables)

| Var | Default | Purpose |
|-----|---------|---------|
| `ANTHROPIC_API_KEY` | — | required |
| `APP_PASSWORD` | unset | if set, web UI requires HTTP Basic Auth (any user, this password) |
| `PORT` | `8000` | port the web app binds (Render sets this automatically) |
| `ANTHROPIC_BASE_URL` | SDK default | enterprise gateway, honored by the SDK |
| `CEDAR_GROVE_MODEL` | `claude-opus-4-7` | model id |
| `CEDAR_GROVE_MAX_TOKENS` | `8000` | response cap |
| `CEDAR_GROVE_API_TIMEOUT` | `600` | per-request timeout (s) |
| `CEDAR_GROVE_API_MAX_RETRIES` | `4` | SDK retry count (handles 429/5xx) |
| `CEDAR_GROVE_EFFORT` | `` (off) | adaptive-thinking effort: low/medium/high/xhigh/max |
| `CEDAR_GROVE_COMPLETENESS_PASS` | `1` (on) | second recall pass; set `0` to disable |
| `CEDAR_GROVE_REDLINE_AUTHOR` | `Michael Ohta` | author stamped on tracked changes |
| `CEDAR_GROVE_SKILL_DIR` | `./skill` | where `SKILL.md` + `PLAYBOOK.md` are mounted |
| `CEDAR_GROVE_OUTPUT_DIR` | project dir | where CLI writes outputs (also `-o`) |

The skill and playbook are read once per process (`lru_cache`), so a long-lived
server doesn't re-read them per request.

## How it works

1. **Extraction.** Every `<w:p>` in the body is indexed in document order, including
   paragraphs inside table cells. The model receives `[¶0] …`, `[¶1] …` and targets
   edits by paragraph number. Extraction and apply share the exact same ordered list
   so indices never drift on schedules / signature blocks.
2. **Claude call.** Skill + playbook live in the system prompt (the playbook is
   cached with a 1-hour TTL — `cache_control: {"type":"ephemeral","ttl":"1h"}` —
   because it's identical across every contract and the default TTL is 5 minutes).
   A single `messages.create` returns the edits JSON. The per-review user message
   instructs a *comprehensive* pass — review every clause and assert every applicable
   playbook position (hold non-negotiables, propose standard fallbacks, add/strengthen
   where the contract is silent or weaker), relaying the playbook's own sequencing
   guidance. This is what gives one direct call the breadth of an agentic reviewer
   without a tool-use loop. (Optional adaptive thinking via `CEDAR_GROVE_EFFORT` is
   available but off by default — it changes edit *selection*, not breadth, and adds
   latency.) See [skill/SKILL.md](skill/SKILL.md).
3. **Validation gate.** Each edit's `find` must occur exactly once in the target
   paragraph (after normalizing smart quotes, em/en dashes, non-breaking spaces, and
   collapsing repeated spaces). Zero matches → flagged. >1 match → flagged.
   Out-of-range paragraph → flagged. We never guess.
4. **Apply.** Edits are grouped by paragraph; all match spans are computed against
   the original text up-front, sorted, and any overlapping span is rejected. Each
   editable region is rebuilt in a single pass that walks the original text and
   emits kept-run fragments and `<w:del>`/`<w:ins>` blocks in order. **No edit ever
   sees a half-modified region.** Kept/deleted text is split at run-formatting
   boundaries so original formatting (e.g. a bold word mid-sentence) survives;
   insertions inherit the formatting of the first run the span overlaps.
5. **Completeness pass.** A second Claude call (same cached playbook) sees the edits
   the main pass already made and proposes ONLY playbook positions it missed; the new
   ones are deduped against the first set and merged. This closes the recall tail
   without a tool-use loop. ~2 calls per review (the 2nd hits the playbook cache).
   Toggle with `CEDAR_GROVE_COMPLETENESS_PASS=0`.
6. **Round-trip check.** The output bytes are reopened to force an XML parse and
   catch malformed output before returning.

## Counterparty redlines (documents that already have tracked changes)

A counterparty's redline arrives *with* their `<w:ins>`/`<w:del>` already in it (the
test ESA has 78 insertions / 58 deletions). The pipeline handles this:

- **The model reviews the current visible text** — counterparty insertions included,
  their deletions excluded — so it redlines what they actually proposed, not a stale
  version.
- **Edits inside the counterparty's inserted text are layered as nested tracked
  changes.** Their `<w:ins>` is split around our change; our deletion is nested in a
  counterparty-authored `<w:ins>` and our replacement added as our own `<w:ins>`.
  Result: `accept-all` shows our edit applied with their insertion kept; `reject-all`
  reverts everything to the true original. (Verified against pandoc accept/reject.)
- **Edits that straddle a tracked-change boundary** (part on clean text, part on an
  existing insertion, or across an existing deletion) are **layered across each side**:
  the edit is decomposed into one deletion per segment it touches plus a single
  insertion, so it applies as nested tracked changes instead of being flagged. This is
  what lets the highest-value clauses (output ownership, subprocessor, termination,
  indemnity) — the ones the counterparty already redlined — get redlined rather than
  skipped. Accept/reject round-trip is verified.
- **What still gets flagged** (never guessed): a `find` that isn't unique, an
  out-of-range paragraph, two edits that overlap in the same paragraph, and the rare
  case of an edit touching a counterparty `<w:ins>` that contains nested content.

## Privacy / ZDR

Before sending real client documents:

- Enable Zero Data Retention on the Anthropic workspace used for this pipeline.
- The pipeline **never logs contract text** — logs carry counts and paragraph
  indices only (token usage is logged at INFO when `-v` / `logging.INFO`). Keep it
  that way if you add logging.

## Design decisions (do not relitigate)

- **Direct `messages.create`, not an agentic harness.** Latency benchmarks pinned
  agent-loop overhead as the bottleneck. Deterministic orchestration in Python is
  fine; runtime tool-use loops are not.
- **Edit-application, not regenerate-and-diff.** The model emits scoped edits keyed
  to paragraph numbers — never the full revised document.
- **`.docx` with native tracked changes, not PDF.** A redline PDF can be a byproduct
  later (`soffice --headless --convert-to pdf`).
- **Hand-rolled OOXML, not python-docx for tracked changes.** python-docx has never
  supported tracked changes; the OOXML patterns are well-defined and lower-risk here.

## Out of scope (TODO)

- `comment_only` edits → Word margin comments (`comments.xml` + range markers as
  siblings of runs, never nested inside them). The `comment` field is already carried
  on each edit for this.
- Clean accepted-version output (the apply-redlines skill produces one); easy to add
  with a `soffice`/`accept-changes` byproduct step.
- The email trigger (Gmail polling / SendGrid inbound) — wraps `review_bytes`.
- Per-section fan-out (one Claude call per playbook section, merged) for broader
  coverage — reverted to a single call for now; can return behind an env flag.

### Web UI MVP limitations

- **The results page embeds the redlined .docx** (base64, ~1.3× its size). The review
  output is small (a few MB), so the page is a few MB — fine on desktop. The benefit:
  no server-side state, so downloads survive restarts/redeploys/scaling.
- **Synchronous request** (~30–60s + free-tier cold start). If Render ever kills long
  requests, the upgrade is an async job + poll. A 502 during a deploy/cold-start is
  expected (the worker is restarting); it clears once the new worker is up.
- **Open access** burns API credits for anyone with the URL; set `APP_PASSWORD`.

## Tests

```
.venv/bin/pytest -q
```

The suite builds fixtures in-process and verifies:

1. An edit whose `find` spans a bold/normal run boundary applies and preserves bold.
2. Two edits in one paragraph both land in the correct positions (the regression).
3. A `find` with multiple matches is flagged; an out-of-range paragraph is flagged.
4. `pandoc --track-changes=accept` yields the edited text; `--track-changes=reject`
   restores the original exactly.
5. `soffice --headless --convert-to pdf` succeeds (skipped if LibreOffice absent).
6. **Counterparty-redline cases:** an edit inside an existing insertion layers
   correctly, a boundary-straddling edit layers across both sides (replace and delete),
   an edit across a counterparty deletion layers, new change-ids don't collide, and the
   real ESA round-trips — all asserted via accept/reject.
7. **Server path:** `review_bytes` is filesystem-free and returns valid docx bytes.

Validity (file opens) is necessary but NOT sufficient — the accept/reject and
nesting tests are what prove the edits are semantically correct.
