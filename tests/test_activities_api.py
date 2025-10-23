from fastapi.testclient import TestClient
import importlib


app_mod = importlib.import_module('src.app')
client = TestClient(app_mod.app)


def test_get_activities():
    resp = client.get('/activities')
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activities
    assert 'Chess Club' in data


def test_signup_and_duplicate():
    email = 'pytest_user@example.com'
    activity = 'Chess Club'

    # Ensure email is not present initially
    resp = client.get('/activities')
    participants = resp.json()[activity]['participants']
    if email in participants:
        # cleanup before test
        app_mod.activities[activity]['participants'].remove(email)

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert 'Signed up' in resp.json().get('message', '')

    # Duplicate signup should fail with 400
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400

    # Cleanup
    if email in app_mod.activities[activity]['participants']:
        app_mod.activities[activity]['participants'].remove(email)


def test_unregister_and_errors():
    email = 'to_remove@example.com'
    activity = 'Programming Class'

    # Ensure participant present
    if email not in app_mod.activities[activity]['participants']:
        app_mod.activities[activity]['participants'].append(email)

    # Now unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert 'Removed' in resp.json().get('message', '')

    # Unregistering again should return 404
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404
