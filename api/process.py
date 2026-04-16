"""
POST /api/process?job_id=...&material=cortenstaal&thickness=3.0
Runs the full AI pipeline synchronously (Vercel is stateless — no background tasks).
Saves results to /tmp so preview.py can read them.
"""
import json
import sys
import os
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Add _lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "_lib"))

from image_processor import process_image
from vectorizer import raster_to_svg
from template_integrator import integrate_silhouette
from validator import FeasibilityValidator
from pricing import calculate_price
from svg_utils import extract_svg_paths, path_complexity_score
import dxf_generator

UPLOAD_DIR = Path("/tmp/vuurkorf_uploads")
OUTPUT_DIR = Path("/tmp/vuurkorf_outputs")
ALLOWED_MATERIALS = {"cortenstaal", "rvs", "zwart_staal"}
ALLOWED_THICKNESSES = {2.0, 3.0, 4.0, 6.0}


def _cors_headers(h):
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")


def _find_uploaded_file(job_id: str):
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        candidate = UPLOAD_DIR / f"{job_id}{ext}"
        if candidate.exists():
            return candidate
    return None


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        _cors_headers(self)
        self.end_headers()

    def do_POST(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        job_id = params.get("job_id", [None])[0]
        material = params.get("material", ["cortenstaal"])[0]
        thickness_str = params.get("thickness", ["3.0"])[0]

        if not job_id:
            self._error(400, "Geen job_id opgegeven.")
            return

        if material not in ALLOWED_MATERIALS:
            self._error(400, f"Ongeldig materiaal '{material}'. Kies uit: {ALLOWED_MATERIALS}")
            return

        try:
            thickness = float(thickness_str)
        except ValueError:
            self._error(400, "Ongeldige dikte waarde.")
            return

        if thickness not in ALLOWED_THICKNESSES:
            self._error(400, f"Ongeldige dikte {thickness}mm. Kies uit: {ALLOWED_THICKNESSES}")
            return

        upload_path = _find_uploaded_file(job_id)
        if not upload_path:
            self._error(404, f"Geen geupload bestand gevonden voor job_id '{job_id}'.")
            return

        try:
            # Step 1: Process image
            image_bytes = upload_path.read_bytes()
            silhouette_png = process_image(image_bytes)
            silhouette_path = OUTPUT_DIR / f"{job_id}_silhouette.png"
            silhouette_path.write_bytes(silhouette_png)

            # Step 2: Vectorize
            customer_svg = raster_to_svg(silhouette_png)
            customer_svg_path = OUTPUT_DIR / f"{job_id}_customer.svg"
            customer_svg_path.write_text(customer_svg, encoding="utf-8")

            # Step 3: Integrate into template
            merged_svg = integrate_silhouette(customer_svg, scale=1.0, offset_x=0.0, offset_y=0.0)
            merged_svg_path = OUTPUT_DIR / f"{job_id}_merged.svg"
            merged_svg_path.write_text(merged_svg, encoding="utf-8")

            # Step 4: Validate
            validator = FeasibilityValidator(thickness=thickness)
            validation_result = validator.validate(customer_svg)

            # Step 5: Price
            paths = extract_svg_paths(customer_svg)
            complexity = path_complexity_score(paths)
            price_result = calculate_price(material, thickness, complexity)

            # Step 6: Generate DXF for laser cutting
            try:
                dxf_bytes = dxf_generator.svg_to_dxf(merged_svg)
                dxf_path = OUTPUT_DIR / f"{job_id}_snijbestand.dxf"
                dxf_path.write_bytes(dxf_bytes)
            except Exception as dxf_err:
                print(f"DXF generation warning: {dxf_err}")

            self._json(200, {
                "job_id": job_id,
                "status": "completed",
                "validation": validation_result,
                "pricing": price_result,
                "complexity_score": complexity,
                "material": material,
                "thickness": thickness,
                "message": "Verwerking voltooid.",
            })

        except Exception as e:
            self._error(500, f"Verwerkingsfout: {str(e)}")

    def _json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        _cors_headers(self)
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status, detail):
        self._json(status, {"error": detail})
