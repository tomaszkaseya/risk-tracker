from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date

# Epic CRUD operations
def get_epics(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Epic).offset(skip).limit(limit).all()

def get_epic(db: Session, epic_id: int):
    return db.query(models.Epic).filter(models.Epic.id == epic_id).first()

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