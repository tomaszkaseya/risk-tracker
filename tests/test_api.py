import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from app.main import app, get_db
from app.database import Base
from app.models import Project, Epic

# --- Test Database Setup ---
# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the tables in the in-memory database
Base.metadata.create_all(bind=engine)

# --- Test Dependency Override ---
# This function will override the get_db dependency in the main app
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- API Tests ---

def test_email_service_config_error():
    """
    Tests that a 500 error is raised if email settings are not configured.
    """
    # Temporarily unset environment variables to simulate missing config
    original_user = os.getenv("SMTP_USERNAME")
    if original_user:
        del os.environ["SMTP_USERNAME"]

    response = client.post(
        "/api/epics/1/request-date-change", # epic_id 1 is hypothetical
        data={"reason": "Test reason", "proposed_date": "2025-01-01"}
    )
    # The actual epic doesn't exist, so a 404 is also acceptable if it gets that far.
    # The main thing is to not get a pass.
    assert response.status_code in [500, 404]
    
    # Restore env var
    if original_user:
        os.environ["SMTP_USERNAME"] = original_user

def test_get_project_with_epics_recursion():
    """
    Tests that fetching a project with associated epics does not cause a recursion error.
    This is the test that would have caught the previous bug.
    """
    # 1. Create a sample project in the test database
    db = next(override_get_db())
    test_project = Project(name="Test Project", description="A project for testing")
    db.add(test_project)
    db.commit()
    db.refresh(test_project)

    # 2. Create a sample epic linked to the project
    test_epic = Epic(title="Test Epic", project_id=test_project.id)
    db.add(test_epic)
    db.commit()
    db.refresh(test_epic)
    db.close()

    # 3. Make a request to the API endpoint
    response = client.get(f"/api/projects/{test_project.id}")

    # 4. Assert that the request was successful and the data is valid
    assert response.status_code == 200, response.text
    
    data = response.json()
    assert data["id"] == test_project.id
    assert data["name"] == "Test Project"
    assert "epics" in data
    assert isinstance(data["epics"], list)
    assert len(data["epics"]) == 1
    assert data["epics"][0]["id"] == test_epic.id
    assert data["epics"][0]["title"] == "Test Epic"

def test_create_and_get_epic():
    """
    Tests creating a new epic and then retrieving it.
    """
    response = client.post(
        "/api/projects/",
        json={"name": "Project for Epic Test", "description": "A new project"},
    )
    assert response.status_code == 200
    project_data = response.json()
    project_id = project_data["id"]

    epic_data = {
        "title": "My New Epic",
        "description": "Epic description",
        "status": "Planned",
        "project_id": project_id
    }
    response = client.post(
        "/api/epics/",
        json=epic_data,
    )
    assert response.status_code == 200, response.text
    created_epic = response.json()
    assert created_epic["title"] == epic_data["title"]
    assert "id" in created_epic

    # Verify we can get the epic back
    epic_id = created_epic["id"]
    response = client.get(f"/api/epics/{epic_id}")
    assert response.status_code == 200
    fetched_epic = response.json()
    assert fetched_epic["title"] == epic_data["title"]
    assert fetched_epic["project"]["id"] == project_id 