"""
Preview router: GET /preview/{job_id}
Returns job status + merged SVG preview content.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.routers.process import jobs_store
from app.models.job import JobStatus

router = APIRouter()

OUTPUT_DIR = Path("/tmp/outputs")


@router.get("/preview/{job_id}")
async def get_preview(job_id: str):
    job = jobs_store.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' niet gevonden.",
        )

    response = {
        "job_id": job_id,
        "status": job.status,
        "step": job.step,
        "error": job.error,
    }

    if job.status == JobStatus.completed and job.result:
        # Read merged SVG content
        merged_path = Path(job.result.get("merged_svg_path", ""))
        if merged_path.exists():
            svg_content = merged_path.read_text(encoding="utf-8")
            response["svg"] = svg_content
        else:
            response["svg"] = None

        response["validation"] = job.result.get("validation", {})
        response["pricing"] = job.result.get("pricing", {})
        response["complexity_score"] = job.result.get("complexity_score", 0)
        response["material"] = job.result.get("material")
        response["thickness"] = job.result.get("thickness")

    return JSONResponse(content=response)


@router.get("/preview/{job_id}/svg")
async def get_preview_svg(job_id: str):
    """Return raw SVG content for embedding."""
    job = jobs_store.get(job_id)
    if not job or job.status != JobStatus.completed:
        raise HTTPException(status_code=404, detail="SVG preview niet beschikbaar.")

    merged_path = Path(job.result.get("merged_svg_path", ""))
    if not merged_path.exists():
        raise HTTPException(status_code=404, detail="SVG bestand niet gevonden.")

    from fastapi.responses import Response
    return Response(
        content=merged_path.read_text(encoding="utf-8"),
        media_type="image/svg+xml",
    )
