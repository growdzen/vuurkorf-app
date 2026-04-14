"""
POST /api/orders  — create a new order
GET  /api/orders  — list all orders
Orders are stored as JSON in /tmp/vuurkorf_orders.json (MVP — ephemeral per cold start).
"""
import json
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

ORDERS_FILE = Path("/tmp/vuurkorf_orders.json")


def _cors_headers(h):
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")


def _load_orders():
    if ORDERS_FILE.exists():
        try:
            return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def _save_orders(orders):
    ORDERS_FILE.write_text(json.dumps(orders, indent=2, ensure_ascii=False), encoding="utf-8")


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        _cors_headers(self)
        self.end_headers()

    def do_GET(self):
        self._json(200, _load_orders())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)

        try:
            order_data = json.loads(body_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._error(400, "Ongeldig JSON-verzoek.")
            return

        required = ["job_id", "name", "email", "material", "thickness"]
        missing = [f for f in required if f not in order_data]
        if missing:
            self._error(400, f"Ontbrekende velden: {missing}")
            return

        # Validate material & thickness
        allowed_materials = {"cortenstaal", "rvs", "zwart_staal"}
        if order_data["material"] not in allowed_materials:
            self._error(400, f"Ongeldig materiaal '{order_data['material']}'.")
            return

        try:
            thickness = float(order_data["thickness"])
        except (ValueError, TypeError):
            self._error(400, "Ongeldige dikte waarde.")
            return

        # Look up pricing from processed output if available
        output_dir = Path("/tmp/vuurkorf_outputs")
        job_id = order_data["job_id"]
        price = order_data.get("price")  # frontend may pass it directly

        order = {
            "id": str(uuid.uuid4()),
            "job_id": job_id,
            "name": order_data["name"],
            "email": order_data["email"],
            "material": order_data["material"],
            "thickness": thickness,
            "scale": float(order_data.get("scale", 1.0)),
            "offset_x": float(order_data.get("offset_x", 0.0)),
            "offset_y": float(order_data.get("offset_y", 0.0)),
            "price": price,
            "status": "confirmed",
            "created_at": datetime.utcnow().isoformat(),
        }

        orders = _load_orders()
        orders.append(order)
        _save_orders(orders)

        self._json(201, {
            "order_id": order["id"],
            "status": "confirmed",
            "price": price,
            "message": f"Bestelling bevestigd! We nemen contact op via {order['email']}.",
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
