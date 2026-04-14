"""
Orders router: POST /orders
Saves order data to a JSON file (MVP — no database needed).
"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.order import OrderCreate, Order
from app.routers.process import jobs_store
from app.models.job import JobStatus

router = APIRouter()

ORDERS_FILE = Path("/home/sprite/vuurkorf/backend/data/orders.json")
ORDERS_FILE.parent.mkdir(parents=True, exist_ok=True)


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
