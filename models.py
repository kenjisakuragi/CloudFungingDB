from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, UniqueConstraint, Index
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Base(DeclarativeBase):
    pass

class Project(Base):
    __tablename__ = 'projects'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_name = Column(String, nullable=False, index=True)
    project_id_on_platform = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    current_amount = Column(Float, nullable=True)
    target_amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    backers_count = Column(Integer, nullable=True)
    end_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('platform_name', 'project_id_on_platform', name='uix_platform_project_id'),
    )

    def __repr__(self):
        return f"<Project(platform='{self.platform_name}', title='{self.title}')>"
