import { useEffect, useState } from "react";
import { useApp } from "../state/AppContext";
import { api } from "../api/client";
import { TrendBar, HorizontalBars } from "../components/Charts";
import { Card, MiniBar, RowLine } from "../components/Ui";
import { trustColor, COLORS } from "../components/theme";

const RANGE_DAYS = { "Last 24 hours": 1, "Last 7 days": 7, "Last 30 days": 30 };

export default function RiskAnalytics() {
  const { userId, orgMode, organization } = useApp();
  const [range, setRange] = useState("Last 7 days");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const days = RANGE_DAYS[range];
    api
      .getAnalytics(userId, { organization: orgMode ? organization : undefined, days })
      .then((res) => { if (!cancelled) setData(res); })
      .catch((err) => { if (!cancelled) setError(err.message); });
    return () => { cancelled = true; };
  }, [userId, orgMode, organization, range]);

  if (error) {
    return (
      <div className="text-[12.5px] text-warn bg-[#3a2a05] border border-[#78350f] rounded-lg px-4 py-2.5">
        Backend not reachable ({error}).
      </div>
    );
  }
  if (!data) return <div className="text-faint text-sm">Loading risk analytics…</div>;

  const riskTrend = data.risk_trend.map((p) => ({
    label: new Date(p.date).toLocaleDateString([], { weekday: "short" }),
    value: p.avg_risk,
  }));
  const riskTypes = data.top_risk_types.map((t) => ({
    label: t.rule_name.replace(/_/g, " "),
    value: t.count,
  }));

  return (
    <div>
      <div className="text-[19px] font-semibold mb-0.5">Risk analytics dashboard</div>
      <div className="text-[12.5px] text-faint mb-4">
        Trends, patterns &amp; insights {data.scope === "organization" ? "— across your organization" : ""}
      </div>

      <select className="input-field w-48 mb-4" value={range} onChange={(e) => setRange(e.target.value)}>
        <option>Last 24 hours</option>
        <option>Last 7 days</option>
        <option>Last 30 days</option>
      </select>

      <div className="grid grid-cols-4 gap-4 mb-4">
        <Card label="Total alerts"><div className="text-2xl font-semibold">{data.total_alerts}</div></Card>
        <Card label="High risk events"><div className="text-2xl font-semibold">{data.high_risk_events}</div></Card>
        <Card label="Users at risk"><div className="text-2xl font-semibold">{data.users_at_risk}</div></Card>
        <Card label="Blocked actions"><div className="text-2xl font-semibold">{data.blocked_actions}</div></Card>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <Card label="Typing — similarity to your own baseline">
          {data.typing_baseline.map((f) => (
            <MiniBar key={f.label} label={f.label} pct={f.pct} color={trustColor(f.pct)} />
          ))}
        </Card>
        <Card label="Mouse — similarity to your own baseline">
          {data.mouse_baseline.map((f) => (
            <MiniBar key={f.label} label={f.label} pct={f.pct} color={trustColor(f.pct)} />
          ))}
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <Card label="Risk trend over time">
          {riskTrend.length ? <TrendBar data={riskTrend} /> : (
            <div className="text-faint text-[12px] py-8 text-center">No risk events recorded in this period yet</div>
          )}
        </Card>
        <Card label="Top risk types">
          {riskTypes.length ? <HorizontalBars data={riskTypes} /> : (
            <div className="text-faint text-[12px] py-8 text-center">No rule triggers recorded in this period yet</div>
          )}
        </Card>
      </div>

      <Card label="Insights">
        {data.insights.average_trust != null ? (
          <>
            <RowLine left="Peak trust" right={data.insights.peak_trust.toFixed(0)} rightColor={COLORS.good} />
            <RowLine left="Lowest trust" right={data.insights.lowest_trust.toFixed(0)} rightColor={COLORS.bad} />
            <RowLine left="Average trust" right={data.insights.average_trust.toFixed(0)} rightColor={COLORS.good} />
          </>
        ) : (
          <div className="text-faint text-[12px]">No trust events recorded in this period yet</div>
        )}
      </Card>
    </div>
  );
}
