from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date
import calendar

# Project CRUD operations
def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_project_by_jira_key(db: Session, jira_project_key: str):
    return db.query(models.Project).filter(models.Project.jira_project_key == jira_project_key).first()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, project: schemas.ProjectUpdate):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        update_data = project.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

# Epic CRUD operations
def get_epics(db: Session, project_id: int = None, status: str = None, quarter: str = None, skip: int = 0, limit: int = 1000):
    query = db.query(models.Epic)
    if project_id:
        query = query.filter(models.Epic.project_id == project_id)
    if status:
        query = query.filter(models.Epic.status == status)
    if quarter and quarter != "":
        try:
            year, q_num = quarter.split('-Q')
            year = int(year)
            q_num = int(q_num)
            
            start_month = (q_num - 1) * 3 + 1
            end_month = q_num * 3
            
            # Get the last day of the end month
            last_day = calendar.monthrange(year, end_month)[1]
            
            start_date = date(year, start_month, 1)
            end_date = date(year, end_month, last_day)

            query = query.filter(models.Epic.target_launch_date.between(start_date, end_date))
        except (ValueError, IndexError):
            # Pass silently if the quarter format is invalid
            pass

    return query.order_by(models.Epic.target_launch_date.desc()).offset(skip).limit(limit).all()

def get_epics_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Epic).filter(models.Epic.project_id == project_id).offset(skip).limit(limit).all()

def get_epic(db: Session, epic_id: int):
    return db.query(models.Epic).filter(models.Epic.id == epic_id).first()

def get_epic_by_jira_key(db: Session, jira_epic_key: str):
    return db.query(models.Epic).filter(models.Epic.jira_epic_key == jira_epic_key).first()

def create_epic(db: Session, epic: schemas.EpicCreate):
    db_epic = models.Epic(**epic.model_dump())
    db.add(db_epic)
    db.commit()
    db.refresh(db_epic)
    return db_epic

def update_epic(db: Session, epic_id: int, epic: schemas.EpicUpdate):
    db_epic = db.query(models.Epic).filter(models.Epic.id == epic_id).first()
    if db_epic:
        update_data = epic.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_epic, key, value)
        db.commit()
        db.refresh(db_epic)
    return db_epic

def delete_epic(db: Session, epic_id: int):
    db_epic = db.query(models.Epic).filter(models.Epic.id == epic_id).first()
    if db_epic:
        db.delete(db_epic)
        db.commit()
        return True
    return False

# Risk CRUD operations
def get_risks_by_epic(db: Session, epic_id: int):
    return db.query(models.Risk).filter(models.Risk.epic_id == epic_id).all()

def get_risk(db: Session, risk_id: int):
    return db.query(models.Risk).filter(models.Risk.id == risk_id).first()

def create_risk(db: Session, risk: schemas.RiskCreate, epic_id: int):
    db_risk = models.Risk(**risk.model_dump(), epic_id=epic_id)
    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)
    return db_risk

def update_risk(db: Session, risk_id: int, risk: schemas.RiskUpdate):
    db_risk = db.query(models.Risk).filter(models.Risk.id == risk_id).first()
    if db_risk:
        update_data = risk.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_risk, key, value)
        db.commit()
        db.refresh(db_risk)
    return db_risk

def delete_risk(db: Session, risk_id: int):
    db_risk = db.query(models.Risk).filter(models.Risk.id == risk_id).first()
    if db_risk:
        db.delete(db_risk)
        db.commit()
        return True
    return False

# Risk Update CRUD operations
def get_risk_updates(db: Session, risk_id: int):
    return db.query(models.RiskUpdate).filter(models.RiskUpdate.risk_id == risk_id).all()

def create_risk_update(db: Session, update: schemas.RiskUpdateCreate, risk_id: int):
    db_update = models.RiskUpdate(**update.model_dump(), risk_id=risk_id)
    db.add(db_update)
    db.commit()
    db.refresh(db_update)
    return db_update 