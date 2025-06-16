from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Epic(Base):
    __tablename__ = "epics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_launch_date = Column(Date, nullable=True)
    actual_launch_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="Planned")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship with risks
    risks = relationship("Risk", back_populates="epic", cascade="all, delete-orphan")

class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    epic_id = Column(Integer, ForeignKey("epics.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    mitigation_plan = Column(Text, nullable=True)
    date_added = Column(Date, nullable=False, server_default=func.current_date())
    status = Column(String(50), nullable=False, default="Open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    epic = relationship("Epic", back_populates="risks")
    updates = relationship("RiskUpdate", back_populates="risk", cascade="all, delete-orphan")

class RiskUpdate(Base):
    __tablename__ = "risk_updates"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risks.id", ondelete="CASCADE"), nullable=False)
    update_text = Column(Text, nullable=False)
    date_added = Column(Date, nullable=False, server_default=func.current_date())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    risk = relationship("Risk", back_populates="updates") 