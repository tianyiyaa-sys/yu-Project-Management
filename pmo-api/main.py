import os
import uuid
from datetime import date, datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Date, DateTime, ForeignKey, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://yu_pmo:yu_pmo_local@pmo-db:5432/yu_pmo",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active")
    customer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    manager: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    project_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    wekan_board_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    rbc_project_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Stage(Base):
    __tablename__ = "project_stages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    planned_due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Risk(Base):
    __tablename__ = "risks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    level: Mapped[str] = mapped_column(String(32), default="mid")
    owner: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open")
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    meeting_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    meeting_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)

app = FastAPI(title="Yu PMO API", version="0.1.0")


class ProjectSyncIn(BaseModel):
    board_id: str
    name: str


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: str
    customer: Optional[str] = None
    manager: Optional[str] = None
    project_type: Optional[str] = None
    wekan_board_id: Optional[str] = None
    rbc_project_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


@app.get("/health")
def health():
    return {"ok": True, "service": "yu-pmo-api"}


@app.get("/api/projects", response_model=list[ProjectOut])
def list_projects():
    with SessionLocal() as session:
        return list(session.scalars(select(Project).order_by(Project.created_at.desc())))


@app.get("/api/projects/by-wekan/{board_id}", response_model=ProjectOut)
def get_project_by_wekan(board_id: str):
    with SessionLocal() as session:
        project = session.scalar(select(Project).where(Project.wekan_board_id == board_id))
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project


@app.post("/api/projects/sync-wekan", response_model=ProjectOut)
def sync_wekan_project(payload: ProjectSyncIn):
    with SessionLocal() as session:
        project = session.scalar(select(Project).where(Project.wekan_board_id == payload.board_id))
        if project:
            if project.name != payload.name:
                project.name = payload.name
                project.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(project)
            return project

        project = Project(
            id=str(uuid.uuid4()),
            name=payload.name,
            wekan_board_id=payload.board_id,
            status="active",
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        return project
