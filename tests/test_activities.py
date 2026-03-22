"""
Comprehensive tests for FastAPI activities API endpoints.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test preconditions and test data
- Act: Execute the API call
- Assert: Verify response codes, content, and side effects
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
    
    def test_get_activities_includes_all_required_fields(self, client, reset_activities):
        """Test that each activity has required fields: description, schedule, max_participants, participants."""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
            assert required_fields.issubset(activity_data.keys()), \
                f"{activity_name} missing required fields. Has: {activity_data.keys()}"
    
    def test_get_activities_returns_activities_as_dict(self, client, reset_activities):
        """Test that activities are returned as a dictionary with activity names as keys."""
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict), "Activities should be returned as a dictionary"
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_participants_is_list(self, client, reset_activities):
        """Test that participants field is a list of email strings."""
        # Arrange & Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            assert isinstance(participants, list), f"{activity_name} participants should be a list"
            for participant in participants:
                assert isinstance(participant, str), f"Participant should be a string (email)"
                assert "@" in participant, f"Participant should be a valid email: {participant}"


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_successful_with_valid_activity_and_new_email(self, client, reset_activities):
        """Test successful signup for a valid activity with a new email."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    
    def test_signup_adds_email_to_participants_list(self, client, reset_activities):
        """Test that signup actually adds the email to the participants list."""
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email in activities[activity_name]["participants"]
    
    def test_signup_fails_with_nonexistent_activity(self, client, reset_activities):
        """Test that signup fails with 404 when activity doesn't exist."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_fails_with_duplicate_email(self, client, reset_activities):
        """Test that signup fails with 400 when email is already registered."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_increases_participant_count(self, client, reset_activities):
        """Test that signup increases the participant count."""
        # Arrange
        activity_name = "Gym Class"
        email = "newstudent@mergington.edu"
        
        # Get initial count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity_name]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        response_after = client.get("/activities")
        final_count = len(response_after.json()[activity_name]["participants"])
        assert final_count == initial_count + 1
    
    def test_signup_allows_same_email_in_different_activities(self, client, reset_activities):
        """Test that the same student email can signup for multiple different activities."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both signups succeeded
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_successful_with_registered_email(self, client, reset_activities):
        """Test successful unregister for a registered email."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    
    def test_unregister_removes_email_from_participants_list(self, client, reset_activities):
        """Test that unregister actually removes the email from the participants list."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_fails_with_nonexistent_activity(self, client, reset_activities):
        """Test that unregister fails with 404 when activity doesn't exist."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_fails_when_email_not_registered(self, client, reset_activities):
        """Test that unregister fails with 400 when email is not registered."""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not registered for this activity"
    
    def test_unregister_decreases_participant_count(self, client, reset_activities):
        """Test that unregister decreases the participant count."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Get initial count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity_name]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        response_after = client.get("/activities")
        final_count = len(response_after.json()[activity_name]["participants"])
        assert final_count == initial_count - 1
    
    def test_unregister_specific_email_only(self, client, reset_activities):
        """Test that unregister removes only the specific email, not other participants."""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        participants = activities[activity_name]["participants"]
        assert email_to_remove not in participants
        assert email_to_keep in participants


class TestSignupUnregisterRoundtrip:
    """Tests for signup followed by unregister (roundtrip) scenarios."""
    
    def test_signup_then_unregister_leaves_activity_available(self, client, reset_activities):
        """Test that after signup and unregister, a student can signup again."""
        # Arrange
        activity_name = "Tennis Club"
        email = "student@mergington.edu"
        
        # Act & Assert - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Signup again
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
    
    def test_multiple_signups_and_unregisters(self, client, reset_activities):
        """Test multiple students signing up and unregistering from the same activity."""
        # Arrange
        activity_name = "Art Studio"
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Act - All signup
        for email in students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are registered
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        for email in students:
            assert email in participants
        
        # Unregister first student
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": students[0]}
        )
        assert response.status_code == 200
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert students[0] not in participants
        assert students[1] in participants
        assert students[2] in participants
