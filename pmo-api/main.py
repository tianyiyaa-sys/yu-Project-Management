import os
import uuid
from datetime import date, datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Date, DateTime, ForeignKey, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://yu_pmo:yu_pmo_local_only@pmo-db:5432/yu_pmo",
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
    legacy_migrated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
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

app = FastAPI(title="Yu PMO API", version="0.2.0")


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
    legacy_migrated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class StageIn(BaseModel):
    name: str
    status: str = "pending"
    planned_due_date: Optional[date] = None
    sort_order: int = 0


class StageOut(StageIn):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    created_at: datetime


class RiskIn(BaseModel):
    title: str
    level: str = "mid"
    owner: Optional[str] = None
    status: str = "open"
    due_date: Optional[date] = None
    source: str = "manual"


class RiskOut(RiskIn):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    created_at: datetime


class MaterialIn(BaseModel):
    name: str
    category: Optional[str] = None
    link: Optional[str] = None
    note: Optional[str] = None


class MaterialOut(MaterialIn):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    created_at: datetime


class DecisionIn(BaseModel):
    meeting_name: Optional[str] = None
    meeting_date: Optional[date] = None
    decision: str
    owner: Optional[str] = None
    due_date: Optional[date] = None
    status: str = "open"


class DecisionOut(DecisionIn):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    created_at: datetime


class LegacyStage(BaseModel):
    name: str
    date: Optional[date] = None
    status: str = "pending"


class LegacyRisk(BaseModel):
    title: str
    level: str = "mid"
    owner: Optional[str] = None
    status: str = "open"
    createdAt: Optional[datetime] = None


class LegacyMaterial(BaseModel):
    name: str
    type: Optional[str] = None
    link: Optional[str] = None
    note: Optional[str] = None
    createdAt: Optional[datetime] = None


class LegacyDecision(BaseModel):
    name: Optional[str] = None
    date: Optional[date] = None
    owner: Optional[str] = None
    deadline: Optional[date] = None
    decision: str
    status: str = "open"
    createdAt: Optional[datetime] = None


class LegacyMigrationIn(BaseModel):
    stages: list[LegacyStage] = []
    risks: list[LegacyRisk] = []
    materials: list[LegacyMaterial] = []
    decisions: list[LegacyDecision] = []


def require_project(session, project_id: str) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.get("/health")
def health():
    return {"ok": True, "service": "yu-pmo-api", "version": "0.2.0"}


@app.get("/api/projects", response_model=list[ProjectOut])
def list_projects():
    with SessionLocal() as session:
        return list(session.scalars(select(Project).order_by(Project.created_at.desc())))


@app.get("/api/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: str):
    with SessionLocal() as session:
        return require_project(session, project_id)


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


@app.get("/api/projects/{project_id}/stages", response_model=list[StageOut])
def list_stages(project_id: str):
    with SessionLocal() as session:
        require_project(session, project_id)
        return list(session.scalars(
            select(Stage).where(Stage.project_id == project_id).order_by(Stage.sort_order, Stage.created_at)
        ))


@app.post("/api/projects/{project_id}/stages", response_model=StageOut)
def create_stage(project_id: str, payload: StageIn):
    with SessionLocal() as session:
        require_project(session, project_id)
        item = Stage(id=str(uuid.uuid4()), project_id=project_id, **payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


@app.delete("/api/stages/{item_id}")
def delete_stage(item_id: str):
    with SessionLocal() as session:
        item = session.get(Stage, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Stage not found")
        session.delete(item)
        session.commit()
        return {"ok": True}


@app.get("/api/projects/{project_id}/risks", response_model=list[RiskOut])
def list_risks(project_id: str):
    with SessionLocal() as session:
        require_project(session, project_id)
        return list(session.scalars(
            select(Risk).where(Risk.project_id == project_id).order_by(Risk.created_at.desc())
        ))


@app.post("/api/projects/{project_id}/risks", response_model=RiskOut)
def create_risk(project_id: str, payload: RiskIn):
    with SessionLocal() as session:
        require_project(session, project_id)
        item = Risk(id=str(uuid.uuid4()), project_id=project_id, **payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


@app.delete("/api/risks/{item_id}")
def delete_risk(item_id: str):
    with SessionLocal() as session:
        item = session.get(Risk, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Risk not found")
        session.delete(item)
        session.commit()
        return {"ok": True}


@app.get("/api/projects/{project_id}/materials", response_model=list[MaterialOut])
def list_materials(project_id: str):
    with SessionLocal() as session:
        require_project(session, project_id)
        return list(session.scalars(
            select(Material).where(Material.project_id == project_id).order_by(Material.created_at.desc())
        ))


@app.post("/api/projects/{project_id}/materials", response_model=MaterialOut)
def create_material(project_id: str, payload: MaterialIn):
    with SessionLocal() as session:
        require_project(session, project_id)
        item = Material(id=str(uuid.uuid4()), project_id=project_id, **payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


@app.delete("/api/materials/{item_id}")
def delete_material(item_id: str):
    with SessionLocal() as session:
        item = session.get(Material, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Material not found")
        session.delete(item)
        session.commit()
        return {"ok": True}


@app.get("/api/projects/{project_id}/decisions", response_model=list[DecisionOut])
def list_decisions(project_id: str):
    with SessionLocal() as session:
        require_project(session, project_id)
        return list(session.scalars(
            select(Decision).where(Decision.project_id == project_id).order_by(Decision.created_at.desc())
        ))


@app.post("/api/projects/{project_id}/decisions", response_model=DecisionOut)
def create_decision(project_id: str, payload: DecisionIn):
    with SessionLocal() as session:
        require_project(session, project_id)
        item = Decision(id=str(uuid.uuid4()), project_id=project_id, **payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


@app.delete("/api/decisions/{item_id}")
def delete_decision(item_id: str):
    with SessionLocal() as session:
        item = session.get(Decision, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Decision not found")
        session.delete(item)
        session.commit()
        return {"ok": True}


@app.post("/api/projects/{project_id}/migrate-local")
def migrate_local(project_id: str, payload: LegacyMigrationIn):
    with SessionLocal() as session:
        project = require_project(session, project_id)
        if project.legacy_migrated_at:
            return {"ok": True, "already_migrated": True}

        for index, x in enumerate(payload.stages):
            session.add(Stage(
                id=str(uuid.uuid4()),
                project_id=project_id,
                name=x.name,
                status=x.status,
                planned_due_date=x.date,
                sort_order=index,
            ))

        for x in payload.risks:
            session.add(Risk(
                id=str(uuid.uuid4()),
                project_id=project_id,
                title=x.title,
                level=x.level,
                owner=x.owner,
                status=x.status,
                source="legacy-local",
                created_at=x.createdAt or datetime.utcnow(),
            ))

        for x in payload.materials:
            session.add(Material(
                id=str(uuid.uuid4()),
                project_id=project_id,
                name=x.name,
                category=x.type,
                link=x.link,
                note=x.note,
                created_at=x.createdAt or datetime.utcnow(),
            ))

        for x in payload.decisions:
            session.add(Decision(
                id=str(uuid.uuid4()),
                project_id=project_id,
                meeting_name=x.name,
                meeting_date=x.date,
                decision=x.decision,
                owner=x.owner,
                due_date=x.deadline,
                status=x.status,
                created_at=x.createdAt or datetime.utcnow(),
            ))

        project.legacy_migrated_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()
        session.commit()
        return {
            "ok": True,
            "already_migrated": False,
            "migrated": {
                "stages": len(payload.stages),
                "risks": len(payload.risks),
                "materials": len(payload.materials),
                "decisions": len(payload.decisions),
            },
        }
