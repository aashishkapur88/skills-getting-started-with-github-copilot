"""Pytest configuration and fixtures for testing the FastAPI app."""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient instance for making API requests."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset activities to original state for test isolation.
    
    This fixture provides a deep copy of the original activities dictionary
    and resets the app's activities to this clean state before each test.
    """
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball league and practice",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Develop tennis skills and participate in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["rachel@mergington.edu", "alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media art",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucy@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performance and script writing",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:45 PM",
            "max_participants": 16,
            "participants": ["maya@mergington.edu"]
        },
        "Science Club": {
            "description": "Experiments, research, and STEM exploration",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["isaac@mergington.edu", "grace@mergington.edu"]
        }
    }
    
    # Clear and reset the app's activities dictionary
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    
    yield
    
    # Cleanup: reset again after test completes
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
