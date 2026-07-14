"""API tests."""

from behavioral_guardian.backend.schemas.models import FeatureVector
from behavioral_guardian.tests.conftest import auth_headers


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_endpoint(client, register_user):
    user = register_user("api_analyze_t")
    payload = FeatureVector(user_id=user["id"]).model_dump()
    response = client.post("/api/v1/analyze", json=payload, headers=auth_headers(user))
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == user["id"]
    assert "identity_trust" in body
    assert "activity_risk" in body


def test_trust_endpoint(client, register_user):
    user = register_user("api_trust_t")
    client.post(
        "/api/v1/analyze",
        json=FeatureVector(user_id=user["id"]).model_dump(),
        headers=auth_headers(user),
    )
    response = client.get(f"/api/v1/trust/{user['id']}", headers=auth_headers(user))
    assert response.status_code == 200
    assert "identity_trust" in response.json()


def test_protected_route_without_token_rejected(client, register_user):
    user = register_user("api_noauth_t")
    response = client.get(f"/api/v1/trust/{user['id']}")
    assert response.status_code in (401, 403)


def test_protected_route_wrong_user_rejected(client, register_user):
    user_a = register_user("api_owner_t")
    user_b = register_user("api_intruder_t")
    response = client.get(f"/api/v1/trust/{user_a['id']}", headers=auth_headers(user_b))
    assert response.status_code == 403
