"""Analytics API tests — verifies real aggregation, not placeholder numbers."""

from behavioral_guardian.tests.conftest import auth_headers


def _analyze(client, user, **overrides):
    payload = {
        "user_id": user["id"],
        "ks_dwell_mean": 120, "ks_flight_mean": 80, "ks_wpm": 65, "ks_error_rate": 0.02,
        "ms_speed_mean": 450, "ms_speed_std": 50, "ms_click_rate": 2.1, "ms_idle_ratio": 0.15,
        "activity_signals": {},
    }
    payload.update(overrides)
    res = client.post("/api/v1/analyze", json=payload, headers=auth_headers(user))
    assert res.status_code == 200, res.text
    return res.json()


def test_analytics_with_no_events_returns_zeros(client, register_user):
    user = register_user("quinn_t")
    res = client.get(f"/api/v1/analytics/{user['id']}", headers=auth_headers(user))
    assert res.status_code == 200
    body = res.json()
    assert body["total_alerts"] == 0
    assert body["high_risk_events"] == 0
    assert body["blocked_actions"] == 0
    assert body["top_risk_types"] == []


def test_analytics_counts_real_triggered_rules(client, register_user):
    user = register_user("ray_t")

    _analyze(client, user)  # normal, no rules
    _analyze(client, user, activity_signals={"usb_insertion": True})
    _analyze(client, user, activity_signals={"usb_insertion": True})
    _analyze(client, user, activity_signals={"download_bytes": 6_000_000_000})

    res = client.get(f"/api/v1/analytics/{user['id']}", headers=auth_headers(user))
    body = res.json()

    rule_counts = {r["rule_name"]: r["count"] for r in body["top_risk_types"]}
    assert rule_counts.get("usb_insertion") == 2
    assert rule_counts.get("download_spike") == 1


def test_analytics_high_risk_event_and_blocked_action_counted(client, register_user):
    user = register_user("sara_t")

    # powershell + cmd + credential_tools together push activity_risk well above 60
    # and the response engine kills the process (a "blocked" action).
    _analyze(client, user, activity_signals={
        "powershell_detected": True, "cmd_detected": True, "credential_tools": True,
    })

    res = client.get(f"/api/v1/analytics/{user['id']}", headers=auth_headers(user))
    body = res.json()
    assert body["high_risk_events"] == 1
    assert body["blocked_actions"] == 1
    assert body["users_at_risk"] == 1


def test_analytics_total_alerts_matches_alerts_endpoint(client, register_user):
    user = register_user("theo_t")
    _analyze(client, user, activity_signals={"usb_insertion": True})
    _analyze(client, user, activity_signals={"registry_persistence": True})

    headers = auth_headers(user)
    analytics = client.get(f"/api/v1/analytics/{user['id']}", headers=headers).json()
    alerts = client.get(f"/api/v1/alerts/{user['id']}", headers=headers).json()
    assert analytics["total_alerts"] == len(alerts)


def test_analytics_organization_scope_aggregates_across_users(client, register_user):
    org = "AnalyticsOrgTest"
    u1 = register_user("uma_t", organization=org)
    u2 = register_user("vic_t", organization=org)
    outsider = register_user("wade_t", organization="SomeOtherOrgEntirely")

    _analyze(client, u1, activity_signals={"usb_insertion": True})
    _analyze(client, u2, activity_signals={"usb_insertion": True})
    _analyze(client, outsider, activity_signals={"usb_insertion": True})

    res = client.get(
        f"/api/v1/analytics/{u1['id']}",
        params={"organization": org},
        headers=auth_headers(u1),
    )
    body = res.json()
    assert body["scope"] == "organization"
    rule_counts = {r["rule_name"]: r["count"] for r in body["top_risk_types"]}
    # exactly 2 (u1 + u2), NOT 3 — the outsider in a different org must not be included
    assert rule_counts.get("usb_insertion") == 2


def test_analytics_baseline_defaults_to_100_with_insufficient_history(client, register_user):
    user = register_user("xena_t")
    res = client.get(f"/api/v1/analytics/{user['id']}", headers=auth_headers(user))
    body = res.json()
    # Fewer than 2 feature vectors -> no fabricated deviation, honest 100% similarity
    assert all(f["pct"] == 100.0 for f in body["typing_baseline"])
    assert all(f["pct"] == 100.0 for f in body["mouse_baseline"])


def test_analytics_days_param_excludes_old_events(client, register_user):
    user = register_user("yara_t")
    _analyze(client, user, activity_signals={"usb_insertion": True})
    headers = auth_headers(user)

    res_recent = client.get(f"/api/v1/analytics/{user['id']}", params={"days": 7}, headers=headers)
    assert res_recent.json()["total_alerts"] >= 1

    # days=0 means "since right now" -> the event we just created is excluded
    res_none = client.get(f"/api/v1/analytics/{user['id']}", params={"days": 0}, headers=headers)
    assert res_none.json()["total_alerts"] == 0
