import logging
import os
from jira import JIRA, JIRAError
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from . import crud, schemas, models

# Load environment variables from .env file
load_dotenv()

JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Configure logging for this module
logger = logging.getLogger(__name__)

def get_jira_client():
    """Establishes a connection to the Jira API and returns a client object."""
    if not all([JIRA_SERVER, JIRA_USERNAME, JIRA_API_TOKEN]):
        logger.error("Jira credentials not found in .env file.")
        return None
    
    try:
        jira_client = JIRA(
            server=JIRA_SERVER,
            basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN)
        )
        # Test connection by getting server info
        jira_client.server_info()
        logger.info(f"Successfully connected to Jira server at {JIRA_SERVER}")
        return jira_client
    except JIRAError as e:
        logger.error(f"Jira connection failed: {e.text}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during Jira connection: {e}")
        return None

def map_jira_status_to_local(jira_status_name):
    """Maps a Jira status name to a local status."""
    
    jira_status_name = jira_status_name.lower()
    
    # This mapping can be customized based on your Jira workflow
    status_mapping = {
        # Jira "To Do" category
        'to do': 'Planned',
        'backlog': 'Planned',
        'new': 'Planned',
        'open': 'Planned',
        
        # Jira "In Progress" category
        'in progress': 'In Progress',
        'in review': 'In Progress',
        'development': 'In Progress',
        
        # Jira "Done" category
        'done': 'Launched',
        'closed': 'Launched',
        'resolved': 'Launched',
        'completed': 'Launched',
        
        # Other common statuses
        'blocked': 'Blocked',
        'on hold': 'Delayed',
        'cancelled': 'Cancelled'
    }
    
    return status_mapping.get(jira_status_name, 'Planned') # Default to 'Planned' if no match

def import_epics_from_jira(db: Session, jira_project_key: str):
    """
    Imports epics from a specified Jira project into the Risk Tracker database.
    """
    jira = get_jira_client()
    if not jira:
        raise ConnectionError("Could not connect to Jira. Check credentials and server URL.")

    # Step 1: Find or Create the Project in the local database
    project = crud.get_project_by_jira_key(db, jira_project_key=jira_project_key)
    if not project:
        try:
            jira_project = jira.project(jira_project_key)
            project_create = schemas.ProjectCreate(
                name=jira_project.name,
                jira_project_key=jira_project.key,
                description=getattr(jira_project, 'description', f"Imported from Jira project {jira_project.key}")
            )
            project = crud.create_project(db, project=project_create)
            logger.info(f"Created new local project '{project.name}'")
        except JIRAError as e:
            if e.status_code == 404:
                raise ValueError(f"Jira project with key '{jira_project_key}' not found.")
            else:
                raise IOError(f"Error fetching project from Jira: {e.text}")

    # Step 2: Fetch epics from Jira
    # Note: Jira's definition of "Epic" can vary. This JQL assumes you use a standard setup
    # where Epics are an issue type. You may need to adjust the JQL query.
    # Common epic type names: "Epic", "Story", etc. We search for 'Epic'.
    try:
        # A more robust JQL to find the Epic issue type name might be needed for some Jira instances.
        # This one assumes the issue type is named 'Epic'.
        jql_query = f'project = "{jira_project_key}" AND issuetype = Epic ORDER BY created DESC'
        epics_from_jira = jira.search_issues(jql_query, maxResults=100) # Capped at 100 for safety
        logger.info(f"Found {len(epics_from_jira)} epics in Jira project '{jira_project_key}'.")
    except JIRAError as e:
         raise IOError(f"Error fetching epics from Jira: {e.text}")

    # Step 3: Upsert (Update or Insert) epics into the local database
    imported_count = 0
    updated_count = 0

    for epic_jira in epics_from_jira:
        jira_key = epic_jira.key
        
        # Check if this epic already exists in our DB
        db_epic = crud.get_epic_by_jira_key(db, jira_epic_key=jira_key)

        # Map Jira fields to our schema
        epic_data = {
            'title': epic_jira.fields.summary,
            'description': getattr(epic_jira.fields, 'description', None),
            'jira_epic_key': jira_key,
            'project_id': project.id,
            'target_launch_date': getattr(epic_jira.fields, 'duedate', None),
            'status': map_jira_status_to_local(epic_jira.fields.status.name)
        }

        if db_epic:
            # Update existing epic
            epic_update_schema = schemas.EpicUpdate(**epic_data)
            crud.update_epic(db, epic_id=db_epic.id, epic=epic_update_schema)
            updated_count += 1
        else:
            # Create new epic
            epic_create_schema = schemas.EpicCreate(**epic_data)
            crud.create_epic(db, epic=epic_create_schema)
            imported_count += 1

    return {
        "project_name": project.name,
        "imported": imported_count,
        "updated": updated_count,
        "total_found": len(epics_from_jira)
    } 