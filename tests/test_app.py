from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def test_root_redirects_to_static_index_html():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data():
    # Arrange / Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "test.student@example.com"
    response_url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(response_url, params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_for_existing_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    response_url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(response_url, params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    response_url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(response_url, params={"email": "student@example.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_succeeds():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    response_url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(response_url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "no.such@student.edu"
    response_url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(response_url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
