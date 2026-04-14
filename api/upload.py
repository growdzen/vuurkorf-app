"""
POST /api/upload
Accepts multipart image upload, saves to /tmp, returns job_id.
Vercel serverless function using BaseHTTPRequestHandler.
"""
import cgi
import json
import uuid
import os
from http.server import BaseHTTPRequestHandler
from pathlib import Path

UPLOAD_DIR = Path("/tmp/vuurkorf_uploads")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _cors_headers(h):
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        _cors_headers(self)
        self.end_headers()

    def do_POST(self):
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        content_type = self.headers.get("Content-Type", "")
        content_length = int(self.headers.get("Content-Length", 0))

        if content_length > MAX_FILE_SIZE:
            self._error(413, f"Bestand te groot. Maximum is 20MB.")
            return

        # Parse multipart form data
        environ = {
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": content_type,
            "CONTENT_LENGTH": str(content_length),
        }

        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ=environ,
            )
        except Exception as e:
            self._error(400, f"Kon formulier niet lezen: {e}")
            return

        if "file" not in form:
            self._error(400, "Geen bestand gevonden in het verzoek. Gebruik 'file' als veldnaam.")
            return

        file_item = form["file"]
        filename = file_item.filename or "upload.jpg"
        ext = Path(filename).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            self._error(400, f"Bestandsextensie '{ext}' niet toegestaan. Gebruik JPG, PNG of WEBP.")
            return

        file_bytes = file_item.file.read()

        if len(file_bytes) > MAX_FILE_SIZE:
            self._error(413, f"Bestand te groot ({len(file_bytes)/1024/1024:.1f}MB). Maximum is 20MB.")
            return

        job_id = str(uuid.uuid4())
        save_path = UPLOAD_DIR / f"{job_id}{ext}"
        save_path.write_bytes(file_bytes)

        self._json(200, {
            "job_id": job_id,
            "filename": filename,
            "size_bytes": len(file_bytes),
            "message": "Bestand succesvol geupload.",
        })

    def _json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        _cors_headers(self)
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status, detail):
        self._json(status, {"error": detail})
