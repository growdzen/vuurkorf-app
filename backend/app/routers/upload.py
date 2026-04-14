"""
Upload router: POST /upload
Accepts JPG/PNG/WEBP images up to 20MB, saves to /tmp/uploads/, returns a job_id.
"""
import os
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/tmp/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Bestandstype '{file.content_type}' niet toegestaan. Gebruik JPG, PNG of WEBP.",
        )

    # Validate extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Bestandsextensie '{ext}' niet toegestaan.",
        )

    # Read and check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Bestand te groot ({len(contents) / 1024 / 1024:.1f}MB). Maximum is 20MB.",
        )

    # Save file with unique job_id
    job_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{job_id}{ext}"
    save_path.write_bytes(contents)

    return JSONResponse(
        status_code=200,
        content={
            "job_id": job_id,
            "filename": file.filename,
            "size_bytes": len(contents),
            "file_path": str(save_path),
            "message": "Bestand succesvol geupload.",
        },
    )
