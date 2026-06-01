"""Hermetic tests for the Flask web UI.

`app.review_bytes` is monkeypatched to a stub so no Claude API call or network access
happens — these test the web layer (routing, upload handling, results page, download,
auth), not the review core (covered elsewhere).
"""

from __future__ import annotations

import importlib
import io
import sys
from pathlib import Path

import pytest
from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app as app_module  # noqa: E402
from review import ReviewResult  # noqa: E402


STUB_BYTES = b"PK\x03\x04stub-docx-bytes"


def _stub_review_bytes(data, *args, **kwargs):
    return ReviewResult(
        redlined_bytes=STUB_BYTES,
        flagged=[{
            "edit": {"para": 21, "type": "replace", "find": "best efforts",
                     "replace": "commercially reasonable efforts", "severity": "high",
                     "comment": "x"},
            "reason": "edit spans an existing tracked-change boundary; needs human review",
        }],
        num_edits_proposed=2,
        num_applied=1,
    )


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "review_bytes", _stub_review_bytes)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def _docx_bytes() -> bytes:
    doc = Document()
    doc.add_paragraph("The term is best efforts to deliver.")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.data == b"ok"


def test_index_shows_upload_form(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"<form" in r.data
    assert b'name="file"' in r.data


def test_review_returns_results_page_with_download(client):
    data = {"file": (io.BytesIO(_docx_bytes()), "contract.docx")}
    r = client.post("/review", data=data, content_type="multipart/form-data")
    assert r.status_code == 200
    body = r.data.decode()
    assert "1</strong> edit applied" in body or "1</strong>" in body
    assert "flagged for human review" in body
    # Download is client-side (no server token route); a button + embedded file.
    assert 'id="dl"' in body
    assert "contract.redlined.docx" in body
    # Flagged row rendered.
    assert "needs human review" in body
    assert "21" in body


def test_results_page_embeds_the_docx_bytes(client):
    """The redlined .docx is embedded (base64) in the page — no server-side store, so
    nothing to 404 after a worker restart/redeploy."""
    import base64 as _b64
    import re

    data = {"file": (io.BytesIO(_docx_bytes()), "contract.docx")}
    r = client.post("/review", data=data, content_type="multipart/form-data")
    body = r.data.decode()
    m = re.search(r'<script id="docx"[^>]*>([^<]+)</script>', body)
    assert m, "expected an embedded base64 docx block"
    assert _b64.b64decode(m.group(1).strip()) == STUB_BYTES
    # No stateful download route exists anymore.
    assert client.get("/download/anything").status_code == 404


def test_non_docx_is_rejected(client):
    data = {"file": (io.BytesIO(b"hello"), "notes.txt")}
    r = client.post("/review", data=data, content_type="multipart/form-data")
    assert r.status_code == 400
    assert b"Only .docx" in r.data


def test_missing_file_is_rejected(client):
    r = client.post("/review", data={}, content_type="multipart/form-data")
    assert r.status_code == 400


def test_missing_api_key_is_reported(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    data = {"file": (io.BytesIO(_docx_bytes()), "contract.docx")}
    r = client.post("/review", data=data, content_type="multipart/form-data")
    assert r.status_code == 500
    assert b"ANTHROPIC_API_KEY" in r.data


def test_basic_auth_when_password_set(monkeypatch):
    """With APP_PASSWORD set, the site requires Basic Auth (health stays open)."""
    monkeypatch.setattr(app_module, "APP_PASSWORD", "s3cret")
    monkeypatch.setattr(app_module, "review_bytes", _stub_review_bytes)
    c = app_module.app.test_client()

    assert c.get("/").status_code == 401
    assert c.get("/healthz").status_code == 200  # health exempt

    import base64
    creds = base64.b64encode(b"user:s3cret").decode()
    ok = c.get("/", headers={"Authorization": f"Basic {creds}"})
    assert ok.status_code == 200

    bad = base64.b64encode(b"user:wrong").decode()
    assert c.get("/", headers={"Authorization": f"Basic {bad}"}).status_code == 401
