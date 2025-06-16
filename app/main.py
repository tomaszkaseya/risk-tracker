from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from . import models, database, crud, schemas, email_service

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Risk Tracker", description="Epic and Risk Management Tool", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Dependency to get database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    epics = crud.get_epics(db)
    return templates.TemplateResponse("index.html", {"request": request, "epics": epics})

@app.get("/api/epics", response_model=list[schemas.Epic])
def get_epics(db: Session = Depends(get_db)):
    return crud.get_epics(db)

@app.post("/api/epics", response_model=schemas.Epic)
def create_epic(epic: schemas.EpicCreate, db: Session = Depends(get_db)):
    return crud.create_epic(db=db, epic=epic)

@app.get("/api/epics/{epic_id}", response_model=schemas.Epic)
def get_epic(epic_id: int, db: Session = Depends(get_db)):
    epic = crud.get_epic(db, epic_id=epic_id)
    if epic is None:
        raise HTTPException(status_code=404, detail="Epic not found")
    return epic

@app.put("/api/epics/{epic_id}", response_model=schemas.Epic)
def update_epic(epic_id: int, epic: schemas.EpicUpdate, db: Session = Depends(get_db)):
    db_epic = crud.update_epic(db, epic_id=epic_id, epic=epic)
    if db_epic is None:
        raise HTTPException(status_code=404, detail="Epic not found")
    return db_epic

@app.delete("/api/epics/{epic_id}")
def delete_epic(epic_id: int, db: Session = Depends(get_db)):
    success = crud.delete_epic(db, epic_id=epic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Epic not found")
    return {"message": "Epic deleted successfully"}

@app.post("/api/epics/{epic_id}/risks", response_model=schemas.Risk)
def create_risk(epic_id: int, risk: schemas.RiskCreate, db: Session = Depends(get_db)):
    return crud.create_risk(db=db, risk=risk, epic_id=epic_id)

@app.get("/api/risks/{risk_id}", response_model=schemas.Risk)
def get_risk(risk_id: int, db: Session = Depends(get_db)):
    risk = crud.get_risk(db, risk_id=risk_id)
    if risk is None:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk

@app.put("/api/risks/{risk_id}", response_model=schemas.Risk)
def update_risk(risk_id: int, risk: schemas.RiskUpdate, db: Session = Depends(get_db)):
    db_risk = crud.update_risk(db, risk_id=risk_id, risk=risk)
    if db_risk is None:
        raise HTTPException(status_code=404, detail="Risk not found")
    return db_risk

@app.delete("/api/risks/{risk_id}")
def delete_risk(risk_id: int, db: Session = Depends(get_db)):
    success = crud.delete_risk(db, risk_id=risk_id)
    if not success:
        raise HTTPException(status_code=404, detail="Risk not found")
    return {"message": "Risk deleted successfully"}

@app.post("/api/risks/{risk_id}/updates", response_model=schemas.RiskUpdate)
def create_risk_update(risk_id: int, update: schemas.RiskUpdateCreate, db: Session = Depends(get_db)):
    return crud.create_risk_update(db=db, update=update, risk_id=risk_id)

@app.post("/api/epics/{epic_id}/request-date-change")
async def request_date_change(
    epic_id: int,
    reason: str = Form(...),
    proposed_date: str = Form(None),
    db: Session = Depends(get_db)
):
    epic = crud.get_epic(db, epic_id=epic_id)
    if epic is None:
        raise HTTPException(status_code=404, detail="Epic not found")
    
    try:
        await email_service.send_date_change_request(epic, reason, proposed_date)
        return {"message": "Date change request sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# HTML Routes for web interface
@app.get("/epics/{epic_id}", response_class=HTMLResponse)
async def epic_detail(request: Request, epic_id: int, db: Session = Depends(get_db)):
    epic = crud.get_epic(db, epic_id=epic_id)
    if epic is None:
        raise HTTPException(status_code=404, detail="Epic not found")
    return templates.TemplateResponse("epic_detail.html", {"request": request, "epic": epic})

@app.get("/epics", response_class=HTMLResponse)
async def epics_list(request: Request, db: Session = Depends(get_db)):
    epics = crud.get_epics(db)
    return templates.TemplateResponse("epics_list.html", {"request": request, "epics": epics})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 