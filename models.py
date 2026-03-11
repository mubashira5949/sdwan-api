from sqlalchemy import Column, Integer, String
from database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, index=True)
    system_ip = Column(String, unique=True, index=True)
    site_id = Column(String, index=True)
    status = Column(String)
    active_config_group = Column(String, nullable=True)
    active_policy = Column(String, nullable=True)
    active_topology = Column(String, nullable=True)

class ConfigGroup(Base):
    __tablename__ = "config_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    policy_type = Column(String, nullable=True) # E.g., Routing, Application Steering, QoS

class Topology(Base):
    __tablename__ = "topologies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String, nullable=False) # E.g., hub-spoke, mesh, hybrid
