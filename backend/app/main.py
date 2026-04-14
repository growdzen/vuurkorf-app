"""
Vuurkorf Personalisatie — FastAPI Backend
Main application entry point.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import upload, process, preview, orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure required directories exist
    Path("/tmp/uploads").mkdir(parents=True, exist_ok=True)
    Path("/tmp/outputs").mkdir(parents=True, exist_ok=True)
    Path("/home/sprite/vuurkorf/backend/data").mkdir(parents=True, exist_ok=True)
    print("Vuurkorf API gestart.")
    yield
    # Shutdown
    print("Vuurkorf API gestopt.")


app = FastAPI(
    title="Vuurkorf Personalisatie API",
    description="AI-gedreven personalisatie van vuurkorven via foto-upload en lasersnijden.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend on localhost:3000 and any sandbox public URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, tags=["Upload"])
app.include_router(process.router, tags=["Process"])
app.include_router(preview.router, tags=["Preview"])
app.include_router(orders.router, tags=["Orders"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Vuurkorf Personalisatie API",
        "version": "1.0.0",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
