from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from database import get_db
from client import SDWANClient
from config import settings

router = APIRouter(prefix="/policies", tags=["Policies"])

sdwan_client = SDWANClient(
    base_url=settings.sdwan_base_url,
    username=settings.sdwan_username,
    password=settings.sdwan_password
)

@router.post("", response_model=schemas.PolicyResponse)
async def create_policy(policy: schemas.PolicyCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new policy in the inventory.
    """
    result = await db.execute(select(models.Policy).filter(models.Policy.name == policy.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Policy with this name already exists")

    new_policy = models.Policy(**policy.model_dump())
    db.add(new_policy)
    await db.commit()
    await db.refresh(new_policy)

    return new_policy

@router.get("", response_model=list[schemas.PolicyResponse])
async def get_policies(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Retrieve all configuration policies.
    """
    result = await db.execute(select(models.Policy).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/deploy")
async def deploy_policy(
    deploy_data: schemas.PolicyDeploy,
    db: AsyncSession = Depends(get_db)
):
    """
    Deploy an active policy prioritizing routing, QoS, or app-steering to target devices.
    """
    # 1. Validate Policy exists locally
    result = await db.execute(select(models.Policy).filter(models.Policy.name == deploy_data.policy_name))
    policy = result.scalars().first()
    if not policy:
        raise HTTPException(status_code=404, detail=f"Policy '{deploy_data.policy_name}' not found")

    if not deploy_data.devices:
        raise HTTPException(status_code=400, detail="Device list cannot be empty")

    # 2. Deploy to SD-WAN
    try:
        await sdwan_client.deploy_policy(deploy_data.policy_name, deploy_data.devices)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deploy policy through SD-WAN: {str(e)}")

    # 3. Update active_policy in local DB for matched devices 
    devices_result = await db.execute(
        select(models.Device).filter(
            (models.Device.hostname.in_(deploy_data.devices)) | 
            (models.Device.system_ip.in_(deploy_data.devices))
        )
    )
    db_devices = devices_result.scalars().all()
    
    for device in db_devices:
        device.active_policy = deploy_data.policy_name

    if db_devices:
        await db.commit()

    return {
        "message": f"Successfully triggered deployment of '{deploy_data.policy_name}'",
        "devices_targeted": len(deploy_data.devices),
        "local_records_updated": len(db_devices)
    }
