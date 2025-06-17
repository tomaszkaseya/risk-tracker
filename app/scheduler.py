import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from . import crud, jira_service
from .database import SessionLocal

# Configure logging
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)

def sync_all_jira_projects():
    """
    A background job that finds all projects linked to Jira and updates them.
    """
    db: Session = SessionLocal()
    try:
        logging.info("--- Starting hourly Jira sync for all linked projects ---")
        
        # Get all projects from the database
        all_projects = crud.get_projects(db, limit=1000) # Assuming max 1000 projects
        
        # Filter for projects that have a Jira key
        jira_projects = [p for p in all_projects if p.jira_project_key]
        
        if not jira_projects:
            logging.info("No Jira-linked projects found to sync.")
            return

        logging.info(f"Found {len(jira_projects)} Jira-linked projects to sync.")
        
        for project in jira_projects:
            try:
                logging.info(f"Syncing project: '{project.name}' (Key: {project.jira_project_key})...")
                result = jira_service.import_epics_from_jira(db, project.jira_project_key)
                logging.info(
                    f"Sync for '{project.name}' complete. "
                    f"Found: {result['total_found']}, "
                    f"Imported: {result['imported']}, "
                    f"Updated: {result['updated']}."
                )
            except Exception as e:
                logging.error(f"Failed to sync project '{project.name}': {e}", exc_info=True)
                
        logging.info("--- Hourly Jira sync finished ---")

    finally:
        db.close()

# Initialize the scheduler
scheduler = BackgroundScheduler(daemon=True)

# Add the job to the scheduler to run every hour
scheduler.add_job(sync_all_jira_projects, 'interval', hours=1) 