from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # ensure some known activities exist
    assert "Chess Club" in data


def test_signup_and_unregister_cycle():
    activity = "Chess Club"
    email = "pytest_user@example.com"

    # Ensure user is not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]

    # Duplicate signup should fail
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400

    # Unregister
    resp3 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp3.status_code == 200
    assert email not in activities[activity]["participants"]


@pytest.mark.parametrize("activity_name,unknown_email", [
    ("Chess Club", "noone@example.com"),
])
def test_unregister_nonexistent_participant(activity_name, unknown_email):
    # Ensure unknown_email is not in the list
    if unknown_email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(unknown_email)

    resp = client.delete(f"/activities/{activity_name}/participants", params={"email": unknown_email})
    assert resp.status_code == 404