"""
Tests for the GET /activities endpoint.

Tests the retrieval of all available activities using the AAA pattern:
- Arrange: Set up test data/state
- Act: Execute the API call
- Assert: Validate the response
"""

import pytest


class TestGetActivities:
    """Test suite for retrieving activities."""

    def test_get_all_activities_success(self, client):
        """
        Test that GET /activities returns all activities successfully.
        
        AAA Pattern:
        - Arrange: No setup needed (activities are pre-populated in app)
        - Act: Make GET request to /activities
        - Assert: Verify status code is 200 and response contains all 10 activities
        """
        # Arrange
        expected_activity_count = 10
        expected_activity_names = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Debate Club",
            "Art Studio",
            "Digital Music Production",
            "Robotics Club",
            "Science Olympiad"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert list(activities.keys()) == expected_activity_names

    def test_get_activities_response_structure(self, client):
        """
        Test that each activity in the response has the correct structure.
        
        AAA Pattern:
        - Arrange: Define required activity fields
        - Act: Make GET request to /activities
        - Assert: Verify each activity has all required fields
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"

    def test_get_activities_response_data_types(self, client):
        """
        Test that activity fields have the correct data types.
        
        AAA Pattern:
        - Arrange: Define expected data types
        - Act: Make GET request to /activities
        - Assert: Verify data types match expectations
        """
        # Arrange
        # Activities should have string descriptions, string schedules,
        # integer max_participants, and list of participants

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            # Each participant should be a string (email)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)

    def test_get_activities_contains_initial_participants(self, client):
        """
        Test that activities contain their initial participants.
        
        AAA Pattern:
        - Arrange: Define expected initial participants for some activities
        - Act: Make GET request to /activities
        - Assert: Verify specific activities have expected participants
        """
        # Arrange
        expected_chess_club_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        expected_programming_participants = ["emma@mergington.edu", "sophia@mergington.edu"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        assert activities["Chess Club"]["participants"] == expected_chess_club_participants
        assert activities["Programming Class"]["participants"] == expected_programming_participants
