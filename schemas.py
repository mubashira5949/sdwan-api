from pydantic import BaseModel

class DeviceBase(BaseModel):
    hostname: str
    system_ip: str
    site_id: str
    status: str

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: int

    class Config:
        from_attributes = True
