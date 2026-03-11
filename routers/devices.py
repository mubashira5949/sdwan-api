from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from database import get_db
from client import SDWANClient
from config import settings

router = APIRouter(prefix="/devices", tags=["Devices"])

# Initialize client (in a real app, this might be a dependency or global instance)
sdwan_client = SDWANClient(
    base_url=settings.sdwan_base_url,
    username=settings.sdwan_username,
    password=settings.sdwan_password
)

@router.post("/onboard", response_model=schemas.DeviceResponse)
async def onboard_device(device: schemas.DeviceCreate, db: AsyncSession = Depends(get_db)):
    """
    Onboards a new device into the local database and the SD-WAN controller.
    """
    # 1. Check if device already exists by system_ip
    result = await db.execute(select(models.Device).filter(models.Device.system_ip == device.system_ip))
    db_device = result.scalars().first()
    if db_device:
        raise HTTPException(status_code=400, detail="Device with this system_ip already exists")

    # 2. Add device to local DB
    new_device = models.Device(**device.model_dump())
    db.add(new_device)
    await db.commit()
    await db.refresh(new_device)

    # 3. Add device to SD-WAN 
    # (In a production scenario, you'd handle rollback if SD-WAN call fails)
    try:
        await sdwan_client.add_device(device)
    except Exception as e:
        # Example rollback (optional for mock, but good practice):
        # await db.delete(new_device)
        # await db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to onboard to SD-WAN: {str(e)}")

    return new_device

@router.get("", response_model=list[schemas.DeviceResponse])
async def get_devices(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Retrieve all devices from the database.
    """
    result = await db.execute(select(models.Device).offset(skip).limit(limit))
    devices = result.scalars().all()
    return devices

@router.get("/{device_id}", response_model=schemas.DeviceResponse)
async def get_device(device_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a specific device by its ID.
    """
    result = await db.execute(select(models.Device).filter(models.Device.id == device_id))
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
