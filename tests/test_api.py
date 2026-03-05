import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Arrange: Setup test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Arrange: Reset activities to initial state before each test"""
    initial_state = {
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
    }
    activities.clear()
    activities.update(initial_state)
    yield
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    def test_get_all_activities_returns_200(self, client, reset_activities):
        """Test: GET /activities returns 200 with all activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert all(activity in response.json() for activity in expected_activities)

    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Test: GET /activities returns correct data structure"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        for activity_name, activity_data in data.items():
            assert all(field in activity_data for field in required_fields)


class TestSignupForActivity:
    def test_signup_student_success(self, client, reset_activities):
        """Test: POST /signup succeeds when student is not registered"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_student_returns_400(self, client, reset_activities):
        """Test: POST /signup returns 400 when student already registered"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already registered for this activity"

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test: POST /signup returns 404 when activity does not exist"""
        # Arrange
        activity_name = "Non-existent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    def test_remove_participant_success(self, client, reset_activities):
        """Test: DELETE /remove succeeds when student is registered"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert email not in activities[activity_name]["participants"]

    def test_remove_nonregistered_student_returns_404(self, client, reset_activities):
        """Test: DELETE /remove returns 404 when student not registered"""
        # Arrange
        activity_name = "Chess Club"
        email = "unregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student not registered for this activity"

    def test_remove_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test: DELETE /remove returns 404 when activity does not exist"""
        # Arrange
        activity_name = "Non-existent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
