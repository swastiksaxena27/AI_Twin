"""Settings API tests — security policy + threshold persistence."""

from behavioral_guardian.tests.conftest import auth_headers


def test_get_settings_creates_defaults_for_new_user(client, register_user):
    user = register_user("liam_t")
    res = client.get(f"/api/v1/settings/{user['id']}", headers=auth_headers(user))
    assert res.status_code == 200
    body = res.json()
    assert body["continuous_monitoring"] is True
    assert body["high_risk_threshold"] == 70


def test_update_settings_persists(client, register_user):
    user = register_user("mia_t")
    headers = auth_headers(user)
    res = client.put(f"/api/v1/settings/{user['id']}", json={
        "high_risk_threshold": 85,
        "block_usb_high_risk": True,
    }, headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["high_risk_threshold"] == 85
    assert body["block_usb_high_risk"] is True

    # fetch again with a brand new request to prove it's stored server-side
    res2 = client.get(f"/api/v1/settings/{user['id']}", headers=headers)
    body2 = res2.json()
    assert body2["high_risk_threshold"] == 85
    assert body2["block_usb_high_risk"] is True


def test_update_settings_partial_update_keeps_other_fields(client, register_user):
    user = register_user("noah_t")
    headers = auth_headers(user)
    client.put(f"/api/v1/settings/{user['id']}", json={"high_risk_threshold": 90}, headers=headers)
    res = client.put(f"/api/v1/settings/{user['id']}", json={"low_risk_threshold": 5}, headers=headers)
    body = res.json()
    assert body["low_risk_threshold"] == 5
    assert body["high_risk_threshold"] == 90  # untouched by the second call


def test_settings_are_isolated_per_user(client, register_user):
    u1 = register_user("olive_t")
    u2 = register_user("pete_t")
    client.put(f"/api/v1/settings/{u1['id']}", json={"high_risk_threshold": 99}, headers=auth_headers(u1))
    res2 = client.get(f"/api/v1/settings/{u2['id']}", headers=auth_headers(u2))
    assert res2.json()["high_risk_threshold"] == 70  # still the default, unaffected by u1's change


def test_cannot_read_another_users_settings(client, register_user):
    owner = register_user("settings_owner_t")
    intruder = register_user("settings_intruder_t")
    res = client.get(f"/api/v1/settings/{owner['id']}", headers=auth_headers(intruder))
    assert res.status_code == 403
