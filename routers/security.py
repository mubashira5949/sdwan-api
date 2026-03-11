from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from database import get_db
from client import SDWANClient
from config import settings

router = APIRouter(prefix="/security", tags=["Security Policies"])

sdwan_client = SDWANClient(
    base_url=settings.sdwan_base_url,
    username=settings.sdwan_username,
    password=settings.sdwan_password
)

@router.post("/policy", response_model=schemas.SecurityPolicyResponse)
async def create_security_policy(policy: schemas.SecurityPolicyCreate, db: AsyncSession = Depends(get_db)):
    """
    Define a new security policy mapping internally.
    """
    result = await db.execute(select(models.SecurityPolicy).filter(models.SecurityPolicy.name == policy.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Security Policy with this name already exists")

    new_policy = models.SecurityPolicy(**policy.model_dump())
    db.add(new_policy)
    await db.commit()
    await db.refresh(new_policy)

    return new_policy

@router.get("/policy", response_model=list[schemas.SecurityPolicyResponse])
async def get_security_policies(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Look up all available security policies (Firewall, IPS, VPN).
    """
    result = await db.execute(select(models.SecurityPolicy).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/deploy")
async def deploy_security_policy(
    deploy_data: schemas.SecurityPolicyDeploy,
    db: AsyncSession = Depends(get_db)
):
    """
    Deploy an active security configuration template binding firewall/VPN specifics to targeted appliances.
    """
    # 1. Verification locally
    result = await db.execute(select(models.SecurityPolicy).filter(models.SecurityPolicy.name == deploy_data.policy))
    policy = result.scalars().first()
    if not policy:
        raise HTTPException(status_code=404, detail=f"Security Policy '{deploy_data.policy}' not found")

    if not deploy_data.devices:
        raise HTTPException(status_code=400, detail="Device payload target cannot be empty")

    # 2. Deploy to external SD-WAN API Simulator
    try:
        await sdwan_client.deploy_security_policy(deploy_data.policy, deploy_data.devices)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to implement security coverage: {str(e)}")

    # 3. Commit status into Postgres records mapping connected structures.
    devices_result = await db.execute(
        select(models.Device).filter(
            (models.Device.hostname.in_(deploy_data.devices)) | 
            (models.Device.system_ip.in_(deploy_data.devices))
        )
    )
    db_devices = devices_result.scalars().all()
    
    for device in db_devices:
        device.active_security_policy = deploy_data.policy

    if db_devices:
        await db.commit()

    return {
        "message": f"Successfully mapped Security Policy {deploy_data.policy}",
        "spokes_targeted": len(deploy_data.devices),
        "local_records_updated": len(db_devices)
    }
