from pydantic import BaseModel

class DeviceBase(BaseModel):
    hostname: str
    system_ip: str
    site_id: str
    status: str

class DeviceCreate(DeviceBase):
    pass

class DeviceConfigDeploy(BaseModel):
    config_group: str

class DeviceResponse(DeviceBase):
    id: int
    active_config_group: str | None = None
    active_policy: str | None = None
    active_topology: str | None = None

    class Config:
        from_attributes = True

class ConfigGroupBase(BaseModel):
    name: str

class ConfigGroupCreate(ConfigGroupBase):
    pass

class ConfigGroupResponse(ConfigGroupBase):
    id: int

    class Config:
        from_attributes = True

class ConfigGroupDeploy(BaseModel):
    group_name: str
    devices: list[str]

class PolicyBase(BaseModel):
    name: str
    policy_type: str | None = None

class PolicyCreate(PolicyBase):
    pass

class PolicyResponse(PolicyBase):
    id: int

    class Config:
        from_attributes = True

class PolicyDeploy(BaseModel):
    policy_name: str
    devices: list[str]

class TopologyBase(BaseModel):
    name: str
    type: str

class TopologyCreate(TopologyBase):
    pass

class TopologyResponse(TopologyBase):
    id: int

    class Config:
        from_attributes = True

class TopologyDeploy(BaseModel):
    type: str
    hub: str | None = None
    spokes: list[str] = []
