import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

import src.app as app_module


# Keep an immutable snapshot of the initial activities so each test gets a clean state
INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


def setup_function():
    # Reset module-level state before each test
    app_module.activities = copy.deepcopy(INITIAL_ACTIVITIES)


def test_root_redirect():
    client = TestClient(app_module.app)
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302, 307, 308)
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities():
    client = TestClient(app_module.app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success_and_duplicate():
    client = TestClient(app_module.app)
    email = "tester@mergington.edu"
    activity = quote("Chess Club", safe="")

    # Successful signup
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]

    # Duplicate signup should fail
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400


def test_signup_nonexistent_activity():
    client = TestClient(app_module.app)
    r = client.post(f"/activities/{quote('NoSuch')}/signup", params={"email": "a@b.com"})
    assert r.status_code == 404


def test_unregister_success_and_not_registered():
    client = TestClient(app_module.app)
    email = "remover@mergington.edu"
    activity = quote("Soccer Team", safe="")

    # Ensure signup then unregister works
    s = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert s.status_code == 200
    assert email in app_module.activities["Soccer Team"]["participants"]

    u = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert u.status_code == 200
    assert email not in app_module.activities["Soccer Team"]["participants"]

    # Unregistering non-registered email fails
    u2 = client.post(f"/activities/{activity}/unregister", params={"email": "noone@x.com"})
    assert u2.status_code == 404
