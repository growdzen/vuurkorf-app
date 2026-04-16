"""
Orders router: POST /orders
Saves order data to a JSON file (MVP — no database needed).
"""
import json
import os
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.order import OrderCreate, Order
from app.routers.process import jobs_store
from app.models.job import JobStatus

router = APIRouter()

_orders_dir = Path(os.environ.get("DATA_DIR", "/tmp/data"))
_orders_dir.mkdir(parents=True, exist_ok=True)
ORDERS_FILE = _orders_dir / "orders.json"


def _load_orders() -> list:
    if ORDERS_FILE.exists():
        try:
            return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def _save_orders(orders: list) -> None:
    ORDERS_FILE.write_text(json.dumps(orders, indent=2, ensure_ascii=False), encoding="utf-8")


@router.post("/orders")
async def create_order(order_data: OrderCreate):
    # Verify job exists and is completed
    job = jobs_store.get(order_data.job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{order_data.job_id}' niet gevonden.",
        )
    if job.status != JobStatus.completed:
        raise HTTPException(
            status_code=400,
            detail=f"Job is nog niet voltooid (status: {job.status}). Wacht tot verwerking klaar is.",
        )

    # Get price from job result
    price = None
    if job.result and "pricing" in job.result:
        price = job.result["pricing"].get("total")

    # Build order
    order = Order(
        id=str(uuid.uuid4()),
        job_id=order_data.job_id,
        name=order_data.name,
        email=order_data.email,
        material=order_data.material,
        thickness=order_data.thickness,
        scale=order_data.scale,
        offset_x=order_data.offset_x,
        offset_y=order_data.offset_y,
        price=price,
        status="confirmed",
    )

    # Save to JSON file
    orders = _load_orders()
    order_dict = order.model_dump()
    order_dict["created_at"] = datetime.utcnow().isoformat()
    orders.append(order_dict)
    _save_orders(orders)

    return JSONResponse(
        status_code=201,
        content={
            "order_id": order.id,
            "status": "confirmed",
            "price": price,
            "message": f"Bestelling bevestigd! We nemen contact op via {order.email}.",
        },
    )


@router.get("/orders")
async def list_orders():
    """List all orders (admin endpoint)."""
    return JSONResponse(content=_load_orders())


@router.get("/orders/{order_id}/dxf")
async def download_dxf(order_id: str):
    """
    Download the DXF cutting file for a specific order.
    Returns the DXF file with proper Content-Disposition headers.
    """
    import os
    from fastapi.responses import FileResponse
    from pathlib import Path

    orders = _load_orders()
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail=f"Bestelling '{order_id}' niet gevonden.")

    # Look up the job to find the DXF file path
    job = jobs_store.get(order["job_id"])
    if not job or not job.result:
        raise HTTPException(status_code=404, detail="DXF bestand niet gevonden.")

    dxf_path_str = job.result.get("dxf_path")
    if not dxf_path_str:
        raise HTTPException(status_code=404, detail="DXF bestand niet beschikbaar voor deze bestelling.")

    dxf_path = Path(dxf_path_str)
    if not dxf_path.exists():
        raise HTTPException(status_code=404, detail="DXF bestand is niet meer beschikbaar op de server.")

    return FileResponse(
        path=str(dxf_path),
        media_type="application/dxf",
        filename=f"vuurkorf_{order_id[:8]}_snijbestand.dxf",
    )
