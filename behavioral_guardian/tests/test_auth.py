"""Auth API tests — register / login."""


def test_register_creates_account(client):
    res = client.post("/api/v1/auth/register", json={
        "username": "alice_t",
        "password": "Secret123!",
        "email": "alice@example.com",
        "full_name": "Alice Test",
        "organization": "Acme",
        "role": "Engineer",
    })
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["user"]["username"] == "alice_t"
    assert body["user"]["full_name"] == "Alice Test"


def test_register_duplicate_rejected(client):
    client.post("/api/v1/auth/register", json={"username": "carol_t", "password": "x"})
    res = client.post("/api/v1/auth/register", json={"username": "carol_t", "password": "y"})
    body = res.json()
    assert body["success"] is False
    assert "already taken" in body["message"].lower()


def test_login_with_correct_password(client, register_user):
    register_user("dave_t", password="Correct123!")
    res = client.post("/api/v1/auth/login", json={"identifier": "dave_t", "password": "Correct123!"})
    body = res.json()
    assert body["success"] is True
    assert body["user"]["username"] == "dave_t"


def test_login_with_email(client, register_user):
    register_user("erin_t", password="Correct123!", email="erin@example.com")
    res = client.post("/api/v1/auth/login", json={"identifier": "erin@example.com", "password": "Correct123!"})
    assert res.json()["success"] is True


def test_login_with_wrong_password_rejected(client, register_user):
    register_user("frank_t", password="Correct123!")
    res = client.post("/api/v1/auth/login", json={"identifier": "frank_t", "password": "WrongPassword"})
    body = res.json()
    assert body["success"] is False
    assert body["user"] is None


def test_login_unknown_user_rejected(client):
    res = client.post("/api/v1/auth/login", json={"identifier": "nobody_here", "password": "x"})
    assert res.json()["success"] is False


def test_device_token_requires_a_valid_login_token(client):
    res = client.post("/api/v1/auth/device-token")
    assert res.status_code in (401, 403)  # no Authorization header at all


def test_device_token_exchange_issues_a_working_long_lived_token(client, register_user):
    """This mirrors what the agent's one-time setup does: log in, then
    immediately trade that token for a device token, then use the device
    token like any other bearer token."""
    from behavioral_guardian.tests.conftest import auth_headers

    user = register_user("device_flow_t")
    res = client.post("/api/v1/auth/device-token", headers=auth_headers(user))
    assert res.status_code == 200
    body = res.json()
    assert body["user_id"] == user["id"]
    assert body["access_token"]
    assert body["access_token"] != user["access_token"]  # a distinct, new token

    # the device token works exactly like the login token on protected routes
    device_headers = {"Authorization": f"Bearer {body['access_token']}"}
    trust_res = client.get(f"/api/v1/trust/{user['id']}", headers=device_headers)
    assert trust_res.status_code == 200
