"""Analytics service — real aggregates over risk/trust/alert/response events.

Nothing here is simulated: every number comes from rows already written by
the trust/risk engines and response engine during /analyze calls.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from behavioral_guardian.backend.schemas.models import (
    AnalyticsInsights,
    AnalyticsResponse,
    BehavioralBaseline,
    RiskTrendPoint,
    RiskTypeCount,
)
from behavioral_guardian.database import repositories as repo

HIGH_RISK_EVENT_THRESHOLD = 60.0
BLOCKING_ACTIONS = {"kill_process", "lock_workstation"}

_TYPING_FEATURES = [
    ("Mean dwell time", "ks_dwell_mean"),
    ("Flight time", "ks_flight_mean"),
    ("Words per minute", "ks_wpm"),
    ("Error rate", "ks_error_rate"),
]
_MOUSE_FEATURES = [
    ("Avg move speed", "ms_speed_mean"),
    ("Speed deviation", "ms_speed_std"),
    ("Click rate", "ms_click_rate"),
    ("Idle ratio", "ms_idle_ratio"),
]


def _similarity(current: float, baseline: float) -> float:
    """100 = matches own historical baseline exactly; lower = more deviation."""
    if baseline in (0, None):
        return 100.0 if current in (0, None) else 0.0
    deviation = abs(current - baseline) / abs(baseline)
    return max(0.0, round(100 - min(100, deviation * 100), 1))


class AnalyticsService:
    """Computes Risk Analytics dashboard data from real stored events."""

    def get_analytics(
        self,
        db: Session,
        user_id: int,
        organization: Optional[str] = None,
        days: int = 7,
    ) -> AnalyticsResponse:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        if organization:
            user_ids = [u.id for u in repo.list_users(db, organization=organization)]
            scope = "organization"
        else:
            user_ids = [user_id]
            scope = "user"
        if not user_ids:
            user_ids = [user_id]

        risk_events = repo.get_risk_events_since(db, user_ids, since)
        trust_events = repo.get_trust_events_since(db, user_ids, since)
        alerts = repo.get_alerts_since(db, user_ids, since)
        responses = repo.get_response_events_since(db, user_ids, since)

        total_alerts = len(alerts)
        high_risk_events = sum(1 for r in risk_events if r.activity_risk >= HIGH_RISK_EVENT_THRESHOLD)
        users_at_risk = len({r.user_id for r in risk_events if r.activity_risk >= HIGH_RISK_EVENT_THRESHOLD})
        blocked_actions = sum(1 for r in responses if r.action in BLOCKING_ACTIONS)

        risk_trend = self._risk_trend(risk_events)
        top_risk_types = self._top_risk_types(risk_events)
        typing_baseline, mouse_baseline = self._baselines(db, user_id)
        insights = self._insights(trust_events)

        return AnalyticsResponse(
            scope=scope,
            days=days,
            total_alerts=total_alerts,
            high_risk_events=high_risk_events,
            users_at_risk=users_at_risk,
            blocked_actions=blocked_actions,
            typing_baseline=typing_baseline,
            mouse_baseline=mouse_baseline,
            risk_trend=risk_trend,
            top_risk_types=top_risk_types,
            insights=insights,
        )

    def _risk_trend(self, risk_events) -> List[RiskTrendPoint]:
        by_day = defaultdict(list)
        for r in risk_events:
            day = r.created_at.strftime("%Y-%m-%d")
            by_day[day].append(r.activity_risk)
        return [
            RiskTrendPoint(date=day, avg_risk=round(sum(vals) / len(vals), 1))
            for day, vals in sorted(by_day.items())
        ]

    def _top_risk_types(self, risk_events) -> List[RiskTypeCount]:
        counts = defaultdict(int)
        for r in risk_events:
            for rule in r.triggered_rules:
                counts[rule.rule_name] += 1
        ranked = sorted(counts.items(), key=lambda kv: -kv[1])[:6]
        return [RiskTypeCount(rule_name=name, count=count) for name, count in ranked]

    def _baselines(self, db: Session, user_id: int):
        vectors = repo.get_feature_vectors(db, user_id, limit=200)
        if len(vectors) < 2:
            # Not enough history yet to establish a personal baseline — neutral 100%
            # rather than fabricating a deviation that hasn't actually been observed.
            typing = [BehavioralBaseline(label=label, pct=100.0) for label, _ in _TYPING_FEATURES]
            mouse = [BehavioralBaseline(label=label, pct=100.0) for label, _ in _MOUSE_FEATURES]
            return typing, mouse

        latest = vectors[0]
        historical = vectors[1:]

        def baseline_avg(attr: str) -> float:
            vals = [getattr(v, attr) for v in historical if getattr(v, attr) is not None]
            return sum(vals) / len(vals) if vals else 0.0

        typing = [
            BehavioralBaseline(label=label, pct=_similarity(getattr(latest, attr) or 0.0, baseline_avg(attr)))
            for label, attr in _TYPING_FEATURES
        ]
        mouse = [
            BehavioralBaseline(label=label, pct=_similarity(getattr(latest, attr) or 0.0, baseline_avg(attr)))
            for label, attr in _MOUSE_FEATURES
        ]
        return typing, mouse

    def _insights(self, trust_events) -> AnalyticsInsights:
        if not trust_events:
            return AnalyticsInsights()
        scores = [t.identity_trust for t in trust_events]
        return AnalyticsInsights(
            peak_trust=max(scores),
            lowest_trust=min(scores),
            average_trust=round(sum(scores) / len(scores), 1),
        )
