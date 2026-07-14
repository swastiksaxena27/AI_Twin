"""Auth protection tests — the gap this fork closes vs. the original AI-twin
backend, where every route past /auth/* was completely open. These prove
every user-scoped route now requires a valid bearer token, and that a token
only grants access to its own user_id (or an org admin's)."""

from behavioral_guardian.tests.conftest import auth_headers

PROTECTED_GET_ROUTES = [
    "/api/v1/trust/{uid}",
    "/api/v1/risk/{uid}",
    "/api/v1/alerts/{uid}",
    "/api/v1/history/{uid}",
    "/api/v1/session/{uid}",
    "/api/v1/settings/{uid}",
    "/api/v1/users/{uid}",
    "/api/v1/analytics/{uid}",
]


def test_login_issues_a_bearer_token(client, register_user):
    user = register_user("token_check_t")
    assert user["access_token"]
    assert isinstance(user["access_token"], str)


def test_every_protected_get_route_rejects_missing_token(client, register_user):
    user = register_user("no_token_sweep_t")
    for template in PROTECTED_GET_ROUTES:
        path = template.format(uid=user["id"])
        res = client.get(path)
        # A missing Authorization header is rejected by FastAPI's HTTPBearer
        # dependency itself, before our own code runs. Different
        # FastAPI/Starlette versions have returned either 401 or 403 for
        # this case over time — both mean "not authenticated", so accept
        # either rather than pinning to one.
        assert res.status_code in (401, 403), f"{path} should require auth, got {res.status_code}"


def test_every_protected_get_route_rejects_other_users_token(client, register_user):
    owner = register_user("sweep_owner_t")
    intruder = register_user("sweep_intruder_t")
    for template in PROTECTED_GET_ROUTES:
        if template == "/api/v1/users/{uid}":
            continue  # covered separately; 404 vs 403 nuance doesn't apply the same way
        path = template.format(uid=owner["id"])
        res = client.get(path, headers=auth_headers(intruder))
        assert res.status_code == 403, f"{path} should reject a foreign token, got {res.status_code}"


def test_org_admin_can_read_teammates_trust_score(client, register_user):
    org = "SweepAdminOrg"
    member = register_user("sweep_member_t", organization=org)
    admin = register_user("sweep_admin_t", organization=org, is_org_admin=True)
    res = client.get(f"/api/v1/trust/{member['id']}", headers=auth_headers(admin))
    assert res.status_code == 200


def test_garbage_token_rejected(client, register_user):
    user = register_user("garbage_token_t")
    res = client.get(f"/api/v1/trust/{user['id']}", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401
