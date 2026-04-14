"""
Process router: POST /process/{job_id}
Starts the AI pipeline as a FastAPI BackgroundTask.
In-memory jobs_store tracks job state.
"""
import os
import glob
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from app.models.job import ProcessingJob, JobStatus, JobStep
from app.services.image_processor import process_image
from app.services.vectorizer import raster_to_svg
from app.services.template_integrator import integrate_silhouette
from app.services.validator import FeasibilityValidator
from app.services.pricing import calculate_price
from app.utils.svg_utils import extract_svg_paths, path_complexity_score

router = APIRouter()

# In-memory job store (MVP — no Redis/Celery needed)
jobs_store: dict[str, ProcessingJob] = {}

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/tmp/uploads"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/tmp/outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _find_uploaded_file(job_id: str) -> str | None:
    """Find the uploaded file for a given job_id."""
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        candidate = UPLOAD_DIR / f"{job_id}{ext}"
        if candidate.exists():
            return str(candidate)
    return None


async def run_pipeline(job_id: str, material: str, thickness: float):
    """
    Full AI processing pipeline, runs as a BackgroundTask.
    Steps: remove_background -> silhouette -> vectorize -> integrate -> validate -> done
    """
    job = jobs_store.get(job_id)
    if not job:
        return

    try:
        # Step 1: Read uploaded file
        file_path = _find_uploaded_file(job_id)
        if not file_path:
            job.status = JobStatus.failed
            job.error = "Geupload bestand niet gevonden."
            jobs_store[job_id] = job
            return

        job.status = JobStatus.processing
        job.step = JobStep.remove_background
        jobs_store[job_id] = job

        # Step 2: Process image (remove bg + silhouette)
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        job.step = JobStep.silhouette
        jobs_store[job_id] = job
        silhouette_png = process_image(image_bytes)

        # Save silhouette PNG
        silhouette_path = OUTPUT_DIR / f"{job_id}_silhouette.png"
        silhouette_path.write_bytes(silhouette_png)

        # Step 3: Vectorize
        job.step = JobStep.vectorize
        jobs_store[job_id] = job
        customer_svg = raster_to_svg(silhouette_png)

        customer_svg_path = OUTPUT_DIR / f"{job_id}_customer.svg"
        customer_svg_path.write_text(customer_svg, encoding="utf-8")

        # Step 4: Integrate into template
        job.step = JobStep.integrate
        jobs_store[job_id] = job
        merged_svg = integrate_silhouette(customer_svg, scale=1.0, offset_x=0.0, offset_y=0.0)

        merged_svg_path = OUTPUT_DIR / f"{job_id}_merged.svg"
        merged_svg_path.write_text(merged_svg, encoding="utf-8")

        # Step 5: Validate feasibility
        job.step = JobStep.validate
        jobs_store[job_id] = job
        validator = FeasibilityValidator(thickness=thickness)
        validation_result = validator.validate(customer_svg)

        # Step 6: Calculate price
        paths = extract_svg_paths(customer_svg)
        complexity = path_complexity_score(paths)
        price_result = calculate_price(material, thickness, complexity)

        # Done
        job.status = JobStatus.completed
        job.step = JobStep.done
        job.result = {
            "merged_svg_path": str(merged_svg_path),
            "customer_svg_path": str(customer_svg_path),
            "silhouette_path": str(silhouette_path),
            "validation": validation_result,
            "pricing": price_result,
            "complexity_score": complexity,
            "material": material,
            "thickness": thickness,
        }
        jobs_store[job_id] = job

    except Exception as exc:
        job = jobs_store.get(job_id, ProcessingJob(id=job_id))
        job.status = JobStatus.failed
        job.error = str(exc)
        jobs_store[job_id] = job
        raise


@router.post("/process/{job_id}")
async def start_processing(
    job_id: str,
    background_tasks: BackgroundTasks,
    material: str = "cortenstaal",
    thickness: float = 3.0,
):
    # Validate material
    allowed_materials = {"cortenstaal", "rvs", "zwart_staal"}
    if material not in allowed_materials:
        raise HTTPException(
            status_code=400,
            detail=f"Ongeldig materiaal '{material}'. Kies uit: {allowed_materials}",
        )

    # Validate thickness
    allowed_thicknesses = {2.0, 3.0, 4.0, 6.0}
    if thickness not in allowed_thicknesses:
        raise HTTPException(
            status_code=400,
            detail=f"Ongeldige dikte {thickness}mm. Kies uit: {allowed_thicknesses}",
        )

    # Check upload exists
    if not _find_uploaded_file(job_id):
        raise HTTPException(
            status_code=404,
            detail=f"Geen geupload bestand gevonden voor job_id '{job_id}'.",
        )

    # Create or reset job
    job = ProcessingJob(id=job_id, status=JobStatus.pending, material=material, thickness=thickness)
    jobs_store[job_id] = job

    # Start background pipeline
    background_tasks.add_task(run_pipeline, job_id, material, thickness)

    return JSONResponse(
        status_code=202,
        content={
            "job_id": job_id,
            "status": "pending",
            "message": "Verwerking gestart.",
        },
    )
