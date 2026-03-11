from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from database import get_db
from client import SDWANClient
from config import settings

router = APIRouter(prefix="/topology", tags=["Topologies"])

sdwan_client = SDWANClient(
    base_url=settings.sdwan_base_url,
    username=settings.sdwan_username,
    password=settings.sdwan_password
)

@router.post("", response_model=schemas.TopologyResponse)
async def create_topology(topology: schemas.TopologyCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a topology rule internally.
    """
    result = await db.execute(select(models.Topology).filter(models.Topology.name == topology.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Topology with this name already exists")

    new_topology = models.Topology(**topology.model_dump())
    db.add(new_topology)
    await db.commit()
    await db.refresh(new_topology)

    return new_topology

@router.get("", response_model=list[schemas.TopologyResponse])
async def get_topologies(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Retrieve all defined topologies.
    """
    result = await db.execute(select(models.Topology).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/deploy")
async def deploy_topology(
    deploy_data: schemas.TopologyDeploy,
    db: AsyncSession = Depends(get_db)
):
    """
    Deploy an active structure logic (hub-spoke, mesh, hybrid).
    """
    if deploy_data.type == "hub-spoke" and not deploy_data.hub:
        raise HTTPException(status_code=400, detail="Hub is required for hub-spoke deployments.")

    # 1. Deploy to SD-WAN Central Controllers
    try:
        await sdwan_client.deploy_topology(
            topology_type=deploy_data.type, 
            hub=deploy_data.hub, 
            spokes=deploy_data.spokes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to implement routing topology: {str(e)}")

    # 2. Update active_topology in local DB for matched devices 
    all_targets = deploy_data.spokes.copy()
    if deploy_data.hub:
        all_targets.append(deploy_data.hub)

    devices_result = await db.execute(
        select(models.Device).filter(
            (models.Device.hostname.in_(all_targets)) | 
            (models.Device.system_ip.in_(all_targets))
        )
    )
    db_devices = devices_result.scalars().all()
    
    for device in db_devices:
        identifier = f"{deploy_data.type}/{deploy_data.hub if deploy_data.hub else 'mesh'}"
        device.active_topology = identifier

    if db_devices:
        await db.commit()

    return {
        "message": f"Successfully triggered topology {deploy_data.type}",
        "spokes_targeted": len(deploy_data.spokes),
        "local_records_updated": len(db_devices)
    }
