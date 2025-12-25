from __future__ import annotations

import datetime
import hashlib
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

ALLOWED_EXTENSIONS = {".dcm", ".nii", ".nii.gz"}
MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024

app = FastAPI(title="MRI Snapshot Analyzer", version="0.1.0")

static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    index_path = static_dir / "index.html"
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_mri(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = file.filename or "upload"
    extension = _extract_extension(filename)
    if extension not in ALLOWED_EXTENSIONS:
        return {
            "status": "error",
            "message": "Unsupported file format. Upload .dcm or .nii/.nii.gz files.",
        }

    raw = await file.read()
    if len(raw) > MAX_FILE_SIZE_BYTES:
        return {
            "status": "error",
            "message": "File too large. Limit is 200MB for the demo endpoint.",
        }

    checksum = hashlib.sha256(raw).hexdigest()
    received_at = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    analysis = _mock_analysis(filename, len(raw))

    return {
        "status": "ok",
        "filename": filename,
        "bytes": len(raw),
        "checksum": checksum,
        "received_at": received_at,
        "analysis": analysis,
    }


def _extract_extension(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".nii.gz"):
        return ".nii.gz"
    return Path(lower).suffix


def _mock_analysis(filename: str, size_bytes: int) -> dict[str, Any]:
    score = (size_bytes % 100) / 100.0
    volume_ml = (size_bytes % 50000) / 1000.0
    return {
        "model": "baseline-mock-v1",
        "confidence": round(score, 2),
        "lesion_volume_ml": round(volume_ml, 2),
        "triage": "review" if score > 0.6 else "routine",
        "notes": f"Demo analysis for {filename}.",
    }
