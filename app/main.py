from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager

from . import models, database, crud, schemas, email_service, jira_service
from .database import engine
from .scheduler import scheduler

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("Application starting up...")
    try:
        scheduler.start()
        logging.info("APScheduler started successfully.")
    except Exception as e:
        logging.error(f"Error starting APScheduler: {e}", exc_info=True)
    
    yield
    
    # Shutdown
    logging.info("Application shutting down...")
    scheduler.shutdown()
    logging.info("APScheduler shut down successfully.")

app = FastAPI(
    title="Risk Tracker", 
    description="Epic and Risk Management Tool", 
    version="1.0.0",
    lifespan=lifespan
)

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    epics = crud.get_epics(db)
    return templates.TemplateResponse("index.html", {"request": request, "epics": epics})

# Project API Routes
@app.get("/api/projects", response_model=list[schemas.Project])
def get_projects(db: Session = Depends(get_db)):
    return crud.get_projects(db)

@app.post("/api/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db=db, project=project)

@app.get("/api/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/api/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = crud.update_project(db, project_id=project_id, project=project)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    success = crud.delete_project(db, project_id=project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

@app.get("/api/projects/{project_id}/epics", response_model=list[schemas.Epic])
def get_project_epics(project_id: int, db: Session = Depends(get_db)):
    # Verify project exists
    project = crud.get_project(db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.get_epics_by_project(db, project_id=project_id)

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
@app.get("/projects", response_class=HTMLResponse)
async def projects_list(request: Request, db: Session = Depends(get_db)):
    projects = crud.get_projects(db)
    return templates.TemplateResponse("projects_list.html", {"request": request, "projects": projects})

@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(request: Request, project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    epics = crud.get_epics_by_project(db, project_id=project_id)
    return templates.TemplateResponse("project_detail.html", {"request": request, "project": project, "epics": epics})

@app.get("/epics/{epic_id}", response_class=HTMLResponse)
async def epic_detail(request: Request, epic_id: int, db: Session = Depends(get_db)):
    epic = crud.get_epic(db, epic_id=epic_id)
    if epic is None:
        raise HTTPException(status_code=404, detail="Epic not found")
    projects = crud.get_projects(db)  # For project dropdown in edit
    return templates.TemplateResponse("epic_detail.html", {"request": request, "epic": epic, "projects": projects})

@app.get("/epics", response_class=HTMLResponse)
async def epics_list(request: Request, project_id: str = None, status: str = None, quarter: str = None, db: Session = Depends(get_db)):
    p_id = None
    if project_id and project_id.isdigit():
        p_id = int(project_id)

    epics = crud.get_epics(db, project_id=p_id, status=status, quarter=quarter)
    projects = crud.get_projects(db)
    statuses = ["Planned", "In Progress", "Blocked", "Delayed", "Launched", "Cancelled"]

    # Generate a list of relevant quarters for the filter
    quarter_set = set()
    # 1. Get quarters from existing epics
    db_epics_with_dates = db.query(models.Epic.target_launch_date).filter(models.Epic.target_launch_date.isnot(None)).distinct().all()
    for (epic_date,) in db_epics_with_dates:
        quarter_set.add(f"{epic_date.year}-Q{(epic_date.month - 1) // 3 + 1}")
    
    # 2. Add current quarter and next 4 quarters to the set
    today = date.today()
    for i in range(5):
        # Move to the middle of the quarter to avoid edge cases with month lengths
        current_date = today + timedelta(days=i * 92) 
        year = current_date.year
        q = (current_date.month - 1) // 3 + 1
        quarter_set.add(f"{year}-Q{q}")
    
    sorted_quarters = sorted(list(quarter_set), reverse=True)

    return templates.TemplateResponse("epics_list.html", {
        "request": request, 
        "epics": epics, 
        "projects": projects,
        "statuses": statuses,
        "quarters": sorted_quarters,
        "selected_project_id": p_id,
        "selected_status": status,
        "selected_quarter": quarter
    })

# Jira Integration API Route
@app.post("/api/jira/import/{jira_project_key}", status_code=200)
def import_jira_project(jira_project_key: str, db: Session = Depends(get_db)):
    try:
        result = jira_service.import_epics_from_jira(db, jira_project_key)
        return result
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IOError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 