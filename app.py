"""
app.py — minimal web UI for the contract-redline pipeline.

Upload a .docx, the pipeline reviews it against the firm playbook, and the page
returns a summary + the flagged edits + a download for the redlined .docx. This is a
thin layer over `review.review_bytes()` — all the real work lives in the review core,
which is stateless and filesystem-free.

Run locally:
    ANTHROPIC_API_KEY=sk-... python app.py            # dev server
    ANTHROPIC_API_KEY=sk-... gunicorn --bind 0.0.0.0:8000 --timeout 120 app:app

On Render: see render.yaml. Set ANTHROPIC_API_KEY (and optionally APP_PASSWORD) as
environment variables in the dashboard.
"""

from __future__ import annotations

import hmac
import logging
import os
import time
import uuid
from pathlib import Path

from flask import (
    Flask,
    Response,
    abort,
    render_template_string,
    request,
)

import anthropic

from review import review_bytes

logger = logging.getLogger("cedar_grove.app")

DOCX_CT = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MAX_UPLOAD_BYTES = 25 * 1024 * 1024          # 25 MB
DOWNLOAD_TTL_SECONDS = 30 * 60               # 30 min
APP_PASSWORD = os.getenv("APP_PASSWORD")     # unset => open access (per design)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

# In-memory download store: token -> {"data": bytes, "name": str, "ts": float}.
# Single-instance / single-worker MVP store. See README "Limitations".
_DOWNLOADS: dict[str, dict] = {}


def _evict_expired() -> None:
    cutoff = time.time() - DOWNLOAD_TTL_SECONDS
    for token in [t for t, v in _DOWNLOADS.items() if v["ts"] < cutoff]:
        _DOWNLOADS.pop(token, None)


# --- Optional Basic Auth ------------------------------------------------------


@app.before_request
def _require_password():
    """If APP_PASSWORD is set, gate everything (except health) behind Basic Auth."""
    if not APP_PASSWORD or request.path == "/healthz":
        return None
    auth = request.authorization
    if auth and hmac.compare_digest(auth.password or "", APP_PASSWORD):
        return None
    return Response(
        "Authentication required.", 401,
        {"WWW-Authenticate": 'Basic realm="Cedar Grove Redline"'},
    )


# --- Templates ----------------------------------------------------------------

_BASE_CSS = """
  body { font-family: -apple-system, system-ui, sans-serif; max-width: 720px;
         margin: 3rem auto; padding: 0 1rem; color: #1a1a1a; line-height: 1.5; }
  h1 { font-size: 1.5rem; } .muted { color: #666; font-size: .9rem; }
  .card { border: 1px solid #ddd; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; }
  .btn { display: inline-block; background: #1a5e3a; color: #fff; padding: .6rem 1.1rem;
         border-radius: 8px; text-decoration: none; border: 0; font-size: 1rem; cursor: pointer; }
  .btn:hover { background: #14492d; }
  table { border-collapse: collapse; width: 100%; margin-top: .5rem; font-size: .9rem; }
  th, td { text-align: left; padding: .4rem .5rem; border-bottom: 1px solid #eee; vertical-align: top; }
  .sev-high { color: #b00; font-weight: 600; } .sev-medium { color: #b56b00; }
  code { background: #f4f4f4; padding: .1rem .3rem; border-radius: 4px; }
  .err { color: #b00; }
"""

_UPLOAD_HTML = """
<!doctype html><html><head><meta charset="utf-8">
<title>Cedar Grove — Contract Redline</title><style>{{ css }}</style></head><body>
  <h1>Cedar Grove — Contract Redline</h1>
  <p class="muted">Upload a <code>.docx</code> contract. It is reviewed against the
  firm playbook and returned with tracked changes you can accept or reject in Word.</p>
  {% if error %}<p class="err">{{ error }}</p>{% endif %}
  <div class="card">
    <form method="post" action="/review" enctype="multipart/form-data">
      <p><input type="file" name="file" accept=".docx" required></p>
      <p><button class="btn" type="submit">Review contract</button></p>
      <p class="muted">A review takes ~30 seconds. Don't close the tab.</p>
    </form>
  </div>
</body></html>
"""

_RESULT_HTML = """
<!doctype html><html><head><meta charset="utf-8">
<title>Redline ready — {{ name }}</title><style>{{ css }}</style></head><body>
  <h1>Redline ready</h1>
  <p class="muted">{{ name }}</p>
  <div class="card">
    <p><strong>{{ applied }}</strong> edit{{ '' if applied == 1 else 's' }} applied,
       <strong>{{ flagged|length }}</strong> flagged for human review.</p>
    <p><a class="btn" href="/download/{{ token }}">Download redlined .docx</a></p>
  </div>
  {% if flagged %}
  <div class="card">
    <h2 style="font-size:1.1rem">Flagged — needs a human</h2>
    <p class="muted">These edits could not be applied safely (ambiguous match or they
    straddle the counterparty's existing tracked changes). Review them by hand.</p>
    <table>
      <tr><th>¶</th><th>Severity</th><th>Reason</th><th>Target text</th></tr>
      {% for f in flagged %}
      <tr>
        <td>{{ f.edit.para }}</td>
        <td class="sev-{{ f.edit.severity }}">{{ f.edit.severity or '—' }}</td>
        <td>{{ f.reason }}</td>
        <td><code>{{ f.edit.find[:80] }}{{ '…' if f.edit.find|length > 80 else '' }}</code></td>
      </tr>
      {% endfor %}
    </table>
  </div>
  {% endif %}
  <p><a href="/">← Review another contract</a></p>
</body></html>
"""


def _render_upload(error: str | None = None, status: int = 200):
    return render_template_string(_UPLOAD_HTML, css=_BASE_CSS, error=error), status


# --- Routes -------------------------------------------------------------------


@app.get("/healthz")
def healthz():
    return "ok", 200


@app.get("/")
def index():
    return _render_upload()


@app.post("/review")
def do_review():
    if not os.getenv("ANTHROPIC_API_KEY"):
        return _render_upload("Server is missing ANTHROPIC_API_KEY.", 500)

    file = request.files.get("file")
    if file is None or not file.filename:
        return _render_upload("Please choose a .docx file.", 400)
    if not file.filename.lower().endswith(".docx"):
        return _render_upload("Only .docx files are supported.", 400)

    data = file.read()
    if not data:
        return _render_upload("The uploaded file was empty.", 400)

    try:
        result = review_bytes(data)
    except anthropic.APIError as exc:
        logger.exception("Claude API error during review")
        return _render_upload(f"Claude API error: {exc}", 502)
    except Exception as exc:  # noqa: BLE001 — surface a friendly message
        logger.exception("review failed")
        return _render_upload(f"Could not process this document: {exc}", 500)

    _evict_expired()
    token = uuid.uuid4().hex
    stem = Path(file.filename).stem
    _DOWNLOADS[token] = {
        "data": result.redlined_bytes,
        "name": f"{stem}.redlined.docx",
        "ts": time.time(),
    }
    logger.info("review complete: applied=%d flagged=%d",
                result.num_applied, result.num_flagged)

    return render_template_string(
        _RESULT_HTML, css=_BASE_CSS, name=file.filename, token=token,
        applied=result.num_applied, flagged=result.flagged,
    )


@app.get("/download/<token>")
def download(token: str):
    _evict_expired()
    entry = _DOWNLOADS.get(token)
    if entry is None:
        abort(404)
    return Response(
        entry["data"], mimetype=DOCX_CT,
        headers={"Content-Disposition": f'attachment; filename="{entry["name"]}"'},
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
