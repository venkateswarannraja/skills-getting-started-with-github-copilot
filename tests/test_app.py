"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


class TestActivities:
    """Tests for activity endpoints"""

    def test_get_activities(self):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert len(activities) == 9

    def test_activity_structure(self):
        """Test that activities have the required structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_activity_has_initial_participants(self):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have initial participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignup:
    """Tests for signup endpoint"""

    def test_signup_for_activity(self):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Art%20Studio/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Art Studio" in data["message"]

    def test_signup_duplicate_participant(self):
        """Test that duplicate signups are rejected"""
        # First signup
        response1 = client.post(
            "/activities/Art%20Studio/signup?email=duplicate@mergington.edu"
        )
        assert response1.status_code == 200

        # Duplicate signup
        response2 = client.post(
            "/activities/Art%20Studio/signup?email=duplicate@mergington.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_updates_participant_list(self):
        """Test that signup updates the participant list"""
        email = "newstudent@mergington.edu"
        activity = "Tennis Club"
        
        # Get initial participant count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity]["participants"])
        
        # Sign up new student
        response2 = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Check updated participant count
        response3 = client.get("/activities")
        updated_count = len(response3.json()[activity]["participants"])
        assert updated_count == initial_count + 1
        assert email in response3.json()[activity]["participants"]


class TestUnregister:
    """Tests for unregister endpoint"""

    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]

    def test_unregister_nonexistent_participant(self):
        """Test unregistering a non-existent participant"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_updates_participant_list(self):
        """Test that unregister updates the participant list"""
        activity = "Music Band"
        email = "noah@mergington.edu"
        
        # Get initial participant count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity]["participants"])
        assert email in response1.json()[activity]["participants"]
        
        # Unregister student
        response2 = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Check updated participant count
        response3 = client.get("/activities")
        updated_count = len(response3.json()[activity]["participants"])
        assert updated_count == initial_count - 1
        assert email not in response3.json()[activity]["participants"]


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_redirect(self):
        """Test that root endpoint redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
