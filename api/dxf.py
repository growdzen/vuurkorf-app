"""
GET /api/dxf?order_id=...&job_id=...
Serves the DXF cutting file for a completed order.
"""
import json
import os
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

OUTPUT_DIR = Path("/tmp/vuurkorf_outputs")
ORDERS_FILE = Path("/tmp/vuurkorf_orders.json")


def _cors_headers(h):
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")


def _load_orders():
    if ORDERS_FILE.exists():
        try:
            return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        _cors_headers(self)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        order_id = params.get("order_id", [None])[0]
        job_id = params.get("job_id", [None])[0]

        if not order_id:
            self._error(400, "Geen order_id opgegeven.")
            return

        # Verify order exists
        orders = _load_orders()
        order = next((o for o in orders if o["id"] == order_id), None)
        if not order:
            self._error(404, f"Bestelling '{order_id}' niet gevonden.")
            return

        # Use job_id from order if not provided
        if not job_id:
            job_id = order.get("job_id")

        if not job_id:
            self._error(400, "Geen job_id beschikbaar voor deze bestelling.")
            return

        dxf_path = OUTPUT_DIR / f"{job_id}_snijbestand.dxf"
        if not dxf_path.exists():
            # Try without the snijbestand suffix
            dxf_path = OUTPUT_DIR / f"{job_id}.dxf"

        if not dxf_path.exists():
            self._error(404, "DXF bestand niet gevonden. Verwerk het bestand eerst via /api/process.")
            return

        dxf_content = dxf_path.read_bytes()

        self.send_response(200)
        self.send_header("Content-Type", "application/dxf")
        self.send_header("Content-Disposition", f'attachment; filename="vuurkorf_{order_id[:8]}_snijbestand.dxf"')
        self.send_header("Content-Length", str(len(dxf_content)))
        _cors_headers(self)
        self.end_headers()
        self.wfile.write(dxf_content)

    def _error(self, status, detail):
        body = json.dumps({"error": detail}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        _cors_headers(self)
        self.end_headers()
        self.wfile.write(body)
