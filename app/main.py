from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.config import settings, logger
from app.services.sdwan_client import sdwan_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up SDWAN API FastAPI application...")
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    await sdwan_client.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="SDWAN API with FastAPI, Postgres Connection, and vManage Client",
    lifespan=lifespan
)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint demonstrating DB setup and SDWAN configuration format."""
    return {"status": "ok", "db": settings.POSTGRES_DB, "sdwan_url": settings.SDWAN_BASE_URL}
