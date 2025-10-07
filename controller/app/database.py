from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Node(Base):
    __tablename__ = "nodes"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    tags = Column(Text)  # JSON string of tags
    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="unknown")  # online, offline, error
    cpu_cores = Column(Integer, default=0)
    memory_gb = Column(Integer, default=0)
    disk_gb = Column(Integer, default=0)


class Instance(Base):
    __tablename__ = "instances"
    
    id = Column(String, primary_key=True, index=True)
    node_id = Column(String, nullable=False, index=True)
    container_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    vehicle_type = Column(String, default="copter")
    model = Column(String, default="iris")
    mav_udp = Column(Integer, nullable=True)
    status = Column(String, default="starting")  # starting, running, stopping, stopped, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
