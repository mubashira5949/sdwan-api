from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from database import get_db
from client import SDWANClient
from config import settings

router = APIRouter(prefix="/config-groups", tags=["Config Groups"])

sdwan_client = SDWANClient(
    base_url=settings.sdwan_base_url,
    username=settings.sdwan_username,
    password=settings.sdwan_password
)

@router.post("", response_model=schemas.ConfigGroupResponse)
async def create_config_group(group: schemas.ConfigGroupCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new configuration group in the inventory.
    """
    result = await db.execute(select(models.ConfigGroup).filter(models.ConfigGroup.name == group.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Config group with this name already exists")

    new_group = models.ConfigGroup(**group.model_dump())
    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)

    return new_group

@router.get("", response_model=list[schemas.ConfigGroupResponse])
async def get_config_groups(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Retrieve all configuration groups.
    """
    result = await db.execute(select(models.ConfigGroup).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/deploy")
async def deploy_config_group(
    deploy_data: schemas.ConfigGroupDeploy,
    db: AsyncSession = Depends(get_db)
):
    """
    Deploy a configuration group to a list of devices (by system_ip or hostname).
    """
    # 1. Validate Config Group exists locally
    result = await db.execute(select(models.ConfigGroup).filter(models.ConfigGroup.name == deploy_data.group_name))
    group = result.scalars().first()
    if not group:
        raise HTTPException(status_code=404, detail=f"Config group '{deploy_data.group_name}' not found")

    if not deploy_data.devices:
        raise HTTPException(status_code=400, detail="Device list cannot be empty")

    # 2. Deploy to SD-WAN
    try:
        await sdwan_client.deploy_group_config(deploy_data.group_name, deploy_data.devices)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deploy group config through SD-WAN: {str(e)}")

    # 3. Update active_config_group in local DB for matched devices 
    # Usually you'd expect system_ip or hostname. Assuming deployment IDs match hostname or system_ip.
    # We update any matching devices locally for consistency.
    devices_result = await db.execute(
        select(models.Device).filter(
            (models.Device.hostname.in_(deploy_data.devices)) | 
            (models.Device.system_ip.in_(deploy_data.devices))
        )
    )
    db_devices = devices_result.scalars().all()
    
    for device in db_devices:
        device.active_config_group = deploy_data.group_name
        device.status = "group_configured"

    if db_devices:
        await db.commit()

    return {
        "message": f"Successfully triggered deployment of '{deploy_data.group_name}'",
        "devices_targeted": len(deploy_data.devices),
        "local_records_updated": len(db_devices)
    }
