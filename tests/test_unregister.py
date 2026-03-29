"""
Tests for the DELETE /activities/{activity_name}/participants endpoint.

Tests student unregistration from activities using the AAA pattern:
- Arrange: Set up test data/state
- Act: Execute the API call
- Assert: Validate the response and side effects
"""

import pytest


class TestUnregisterFromActivity:
    """Test suite for student unregistration functionality."""

    def test_unregister_success_valid_activity_and_participant(self, client):
        """
        Test successful unregistration of a student from an activity.
        
        AAA Pattern:
        - Arrange: Define valid activity and existing participant
        - Act: Make DELETE request to unregister endpoint
        - Assert: Verify status code is 200 and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"  # Already a participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {student_email} from {activity_name}"

    def test_unregister_student_removed_from_participants(self, client):
        """
        Test that student is actually removed from participants list after unregister.
        
        AAA Pattern:
        - Arrange: Define activity and existing participant
        - Act: Unregister student, then fetch activities to verify
        - Assert: Verify student email no longer appears in participants list
        """
        # Arrange
        activity_name = "Programming Class"
        student_email = "emma@mergington.edu"  # Already a participant

        # Act
        unregister_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": student_email}
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()

        # Assert
        assert unregister_response.status_code == 200
        assert student_email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Test that attempting to unregister from a nonexistent activity returns 404.
        
        AAA Pattern:
        - Arrange: Define a nonexistent activity name
        - Act: Attempt to unregister from nonexistent activity
        - Assert: Verify 404 status code and error message
        """
        # Arrange
        activity_name = "Lunch Club"
        student_email = "jack@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """
        Test that attempting to unregister a non-participant returns 404.
        
        AAA Pattern:
        - Arrange: Define existing activity and non-participant email
        - Act: Attempt to unregister non-participant
        - Assert: Verify 404 status code and participant not found message
        """
        # Arrange
        activity_name = "Tennis Club"
        student_email = "karen@mergington.edu"  # Not a participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in this activity"

    def test_unregister_from_activity_with_multiple_participants(self, client):
        """
        Test unregistering one student doesn't affect other participants.
        
        AAA Pattern:
        - Arrange: Define activity with multiple participants, select one to remove
        - Act: Unregister selected student
        - Assert: Verify only selected student is removed, others remain
        """
        # Arrange
        activity_name = "Art Studio"
        student_to_remove = "isabella@mergington.edu"
        other_student = "grace@mergington.edu"

        # Get initial state
        activities_response = client.get("/activities")
        initial_participants = activities_response.json()[activity_name]["participants"].copy()

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": student_to_remove}
        )
        activities_response = client.get("/activities")
        final_participants = activities_response.json()[activity_name]["participants"]

        # Assert
        assert response.status_code == 200
        assert student_to_remove not in final_participants
        assert other_student in final_participants

    def test_unregister_activity_name_case_sensitive(self, client):
        """
        Test that activity names are case-sensitive in unregister requests.
        
        AAA Pattern:
        - Arrange: Define activity name with different capitalization
        - Act: Attempt to unregister using wrong case
        - Assert: Verify 404 is returned (activity not found)
        """
        # Arrange
        activity_name = "robotics club"  # lowercase instead of "Robotics Club"
        student_email = "tyler@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_then_signup_again(self, client):
        """
        Test that a student can unregister and then sign up again for the same activity.
        
        AAA Pattern:
        - Arrange: Define activity and student email
        - Act: Unregister the student, then sign them up again
        - Assert: Verify student is in participants after second signup
        """
        # Arrange
        activity_name = "Debate Club"
        student_email = "lucas@mergington.edu"  # Already a participant

        # Act - First unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": student_email}
        )
        assert unregister_response.status_code == 200

        # Act - Then sign up again
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        assert signup_response.status_code == 200

        # Get final state
        activities_response = client.get("/activities")
        final_participants = activities_response.json()[activity_name]["participants"]

        # Assert
        assert student_email in final_participants

    def test_unregister_single_participant_from_activity(self, client):
        """
        Test unregistering the only participant from an activity.
        
        AAA Pattern:
        - Arrange: Define activity with single participant
        - Act: Unregister that participant
        - Assert: Verify activity now has empty participants list
        """
        # Arrange
        activity_name = "Digital Music Production"
        student_email = "ryan@mergington.edu"  # Only participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": student_email}
        )
        activities_response = client.get("/activities")
        final_participants = activities_response.json()[activity_name]["participants"]

        # Assert
        assert response.status_code == 200
        assert len(final_participants) == 0

    def test_unregister_attempt_from_empty_activity_returns_404(self, client):
        """
        Test that attempting to unregister from an activity with no participants returns 404.
        
        AAA Pattern:
        - Arrange: First unregister all participants from an activity
        - Act: Attempt to unregister another (non-existent) participant
        - Assert: Verify 404 is returned
        """
        # Arrange
        activity_name = "Digital Music Production"
        first_student = "ryan@mergington.edu"
        second_student = "leo@mergington.edu"

        # Setup: Remove the only participant
        client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": first_student}
        )

        # Act - Try to unregister from now-empty activity
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": second_student}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in this activity"
