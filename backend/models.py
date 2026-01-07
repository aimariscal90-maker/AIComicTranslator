from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Integer
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pages = relationship("Page", back_populates="project", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "pages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_url = Column(String, nullable=True)
    final_url = Column(String, nullable=True)
    debug_url = Column(String, nullable=True)
    clean_url = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    page_number = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="pages")
    bubbles = relationship("Bubble", back_populates="page", cascade="all, delete-orphan")

class Bubble(Base):
    __tablename__ = "bubbles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    page_id = Column(String, ForeignKey("pages.id"), nullable=False)
    bbox = Column(JSON, nullable=False)  # [x1, y1, x2, y2]
    original_text = Column(Text, nullable=True)
    translated_text = Column(Text, nullable=True)
    font = Column(String, default="ComicNeue")
    confidence = Column(Integer, nullable=True)
    bubble_type = Column(String, default="speech")  # speech, thought, shout, narrator
    translation_provider = Column(String, nullable=True)
    
    # Relationships
    page = relationship("Page", back_populates="bubbles")
