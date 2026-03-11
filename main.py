from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from config import settings
from logger import logger
from database import engine, Base, get_db
from client import SDWANClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they do not exist
    logger.info("Starting up FastAPI application...")
    try:
        async with engine.begin() as conn:
            # For a basic app without models this just ensures DB connection works
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created or verified.")
    except Exception as e:
        logger.error(f"Error during database startup: {e}")
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    await engine.dispose()

app = FastAPI(
    title=settings.app_name,
    description="FastAPI application with PostgreSQL and SDWAN integration",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """
    Root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the SDWAN API"}

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint that verifies the database connection.
    """
    try:
        # Check database connectivity
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f"failed - {str(e)}"

    return {
        "status": "ok",
        "database": db_status
    }

@app.post("/sdwan/login")
async def sdwan_login():
    """
    Example endpoint showing how to use the SDWANClient to login.
    """
    client = SDWANClient(
        base_url=settings.sdwan_base_url,
        username=settings.sdwan_username,
        password=settings.sdwan_password
    )
    try:
        cookies = await client.login()
        # You would typically convert cookies to dict or handle appropriately
        cookie_dict = dict(cookies)
        return {
            "status": "success", 
            "message": "Logged in successfully",
            "cookies_received": len(cookie_dict) > 0
        }
    except Exception as e:
        logger.error(f"SDWAN login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
