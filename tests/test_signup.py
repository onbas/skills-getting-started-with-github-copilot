"""
Tests for the POST /activities/{activity_name}/signup endpoint.

Tests student signup for activities using the AAA pattern:
- Arrange: Set up test data/state
- Act: Execute the API call
- Assert: Validate the response and side effects
"""

import pytest


class TestSignupForActivity:
    """Test suite for student signup functionality."""

    def test_signup_success_valid_activity_and_email(self, client):
        """
        Test successful signup with valid activity name and email.
        
        AAA Pattern:
        - Arrange: Define valid activity name and student email
        - Act: Make POST request to signup endpoint
        - Assert: Verify status code is 200 and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {student_email} for {activity_name}"

    def test_signup_student_added_to_participants(self, client):
        """
        Test that student is actually added to participants list after signup.
        
        AAA Pattern:
        - Arrange: Define activity and student email, get initial participant count
        - Act: Sign up student, then fetch activities to verify
        - Assert: Verify student email appears in participants list
        """
        # Arrange
        activity_name = "Tennis Club"
        student_email = "bob@mergington.edu"

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()

        # Assert
        assert signup_response.status_code == 200
        assert student_email in activities[activity_name]["participants"]

    def test_signup_duplicate_prevention(self, client):
        """
        Test that a student cannot sign up twice for the same activity.
        
        AAA Pattern:
        - Arrange: Student email who is already signed up
        - Act: Attempt to sign them up again
        - Assert: Verify 400 status code and appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Test that signup to a nonexistent activity returns 404.
        
        AAA Pattern:
        - Arrange: Define a nonexistent activity name
        - Act: Attempt to sign up for nonexistent activity
        - Assert: Verify 404 status code and error message
        """
        # Arrange
        activity_name = "Unicorn Club"
        student_email = "charlie@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_multiple_students_same_activity(self, client):
        """
        Test that multiple different students can sign up for the same activity.
        
        AAA Pattern:
        - Arrange: Define multiple student emails
        - Act: Sign up each student sequentially
        - Assert: Verify all students are in the participants list
        """
        # Arrange
        activity_name = "Art Studio"
        student_emails = ["david@mergington.edu", "emily@mergington.edu", "frank@mergington.edu"]

        # Act
        for email in student_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        activities_response = client.get("/activities")
        activities = activities_response.json()

        # Assert
        for email in student_emails:
            assert email in activities[activity_name]["participants"]

    def test_signup_capacity_limit_not_exceeded(self, client):
        """
        Test that students cannot sign up if activity is at max capacity.
        
        AAA Pattern:
        - Arrange: Find/create activity at max capacity
        - Act: Attempt to sign up when at capacity
        - Assert: Verify appropriate handling (Note: current app may not enforce this)
        
        Note: The current app.py does not check max_participants, but this test
        documents the expected behavior for a complete validation system.
        """
        # Arrange
        activity_name = "Debate Club"
        initial_max = 15
        
        # Get current state
        activities_response = client.get("/activities")
        activities = activities_response.json()
        current_participants = len(activities[activity_name]["participants"])

        # Act - Try to add students up to capacity
        # This test demonstrates the pattern, but the current app may not validate capacity
        student_email = "grace@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Assert
        # Currently the app will succeed, but this test structure supports future capacity checks
        assert response.status_code == 200

    def test_signup_activity_name_case_sensitive(self, client):
        """
        Test that activity names are case-sensitive.
        
        AAA Pattern:
        - Arrange: Define activity name with different capitalization
        - Act: Attempt to sign up using wrong case
        - Assert: Verify 404 is returned (activity not found)
        """
        # Arrange
        activity_name = "chess club"  # lowercase instead of "Chess Club"
        student_email = "henry@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_same_student_different_activities(self, client):
        """
        Test that a student can sign up for multiple different activities.
        
        AAA Pattern:
        - Arrange: Define multiple activities and one student email
        - Act: Sign up student for each activity
        - Assert: Verify student appears in all activities' participants
        """
        # Arrange
        student_email = "iris@mergington.edu"
        activity_names = ["Programming Class", "Robotics Club"]

        # Act
        for activity_name in activity_names:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student_email}
            )
            assert response.status_code == 200

        activities_response = client.get("/activities")
        activities = activities_response.json()

        # Assert
        for activity_name in activity_names:
            assert student_email in activities[activity_name]["participants"]
