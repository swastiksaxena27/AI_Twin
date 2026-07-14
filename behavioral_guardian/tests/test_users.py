"""Users API tests — roster, single profile, profile update."""

from behavioral_guardian.tests.conftest import auth_headers


def test_list_users_includes_registered_user(client, register_user):
    user = register_user("gina_t", organization="Initech", role="QA")
    res = client.get("/api/v1/users", headers=auth_headers(user))
    assert res.status_code == 200
    usernames = [u["username"] for u in res.json()]
    assert "gina_t" in usernames


def test_list_users_filtered_by_organization(client, register_user):
    hank = register_user("hank_t", organization="OnlyHankOrg", role="Ops")
    register_user("ivan_t", organization="SomeOtherOrg", role="Ops")
    # hank isn't an org admin, so he's scoped to his own org regardless of
    # what `organization` he asks for — which happens to match this test.
    res = client.get("/api/v1/users", params={"organization": "OnlyHankOrg"}, headers=auth_headers(hank))
    body = res.json()
    usernames = [u["username"] for u in body]
    assert "hank_t" in usernames
    assert "ivan_t" not in usernames


def test_user_profile_includes_trust_and_risk_fields(client, register_user):
    user = register_user("judy_t")
    res = client.get(f"/api/v1/users/{user['id']}", headers=auth_headers(user))
    assert res.status_code == 200
    body = res.json()
    assert "identity_trust" in body
    assert "activity_risk" in body
    assert "status_level" in body


def test_get_unknown_user_404s(client, register_user):
    admin = register_user("get_admin_t", is_org_admin=True)
    res = client.get("/api/v1/users/999999", headers=auth_headers(admin))
    assert res.status_code == 404


def test_patch_user_updates_profile(client, register_user):
    user = register_user("karl_t")
    headers = auth_headers(user)
    res = client.patch(f"/api/v1/users/{user['id']}", json={
        "full_name": "Karl Updated",
        "device_name": "Karl's Laptop",
    }, headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["full_name"] == "Karl Updated"
    assert body["device_name"] == "Karl's Laptop"

    # confirm it actually persisted, not just echoed back
    res2 = client.get(f"/api/v1/users/{user['id']}", headers=headers)
    assert res2.json()["full_name"] == "Karl Updated"


def test_patch_unknown_user_404s(client, register_user):
    admin = register_user("patch_admin_t", is_org_admin=True)
    res = client.patch("/api/v1/users/999999", json={"full_name": "Nobody"}, headers=auth_headers(admin))
    assert res.status_code == 404


def test_user_cannot_view_another_users_profile(client, register_user):
    owner = register_user("profile_owner_t")
    intruder = register_user("profile_intruder_t")
    res = client.get(f"/api/v1/users/{owner['id']}", headers=auth_headers(intruder))
    assert res.status_code == 403


def test_org_admin_can_view_any_users_profile(client, register_user):
    org = "AdminViewOrg"
    member = register_user("admin_view_member_t", organization=org)
    admin = register_user("admin_view_admin_t", organization=org, is_org_admin=True)
    res = client.get(f"/api/v1/users/{member['id']}", headers=auth_headers(admin))
    assert res.status_code == 200
