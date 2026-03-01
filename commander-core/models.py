from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base

class EventDB(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    start_date = Column(String, index=True, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=True)
    description = Column(String, nullable=False)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemLogDB(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    action_type = Column(String, index=True, nullable=False) # e.g., 'calendar_update', 'memory_save', 'file_edit'
    details = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SettingDB(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
