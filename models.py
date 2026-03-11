from sqlalchemy import Column, Integer, String
from database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, index=True)
    system_ip = Column(String, unique=True, index=True)
    site_id = Column(String, index=True)
    status = Column(String)
