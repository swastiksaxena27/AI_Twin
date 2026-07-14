import { useApp } from "../state/AppContext";
import { useUserData } from "../api/useUserData";
import Gauge from "../components/Gauge";
import { TrendChart } from "../components/Charts";
import { Card, Pill, MiniBar, RowLine } from "../components/Ui";
import { trustColor, riskColor, statusPillInfo } from "../components/theme";

export default function DashboardPersonal() {
  const { fullName, userId } = useApp();
  const { trust, risk, alerts, history, error } = useUserData(userId, { poll: 15000 });

  const trustVal = trust?.identity_trust ?? 0;
  const riskVal = risk?.activity_risk ?? 0;
  const status = trust?.status_level ?? "UNKNOWN";
  const statusInfo = statusPillInfo(status);
  const rows = history?.trust_history ?? [];

  const factors = { "Typing pattern": 90, "Mouse movement": 88, "Application usage": 75, "Activity rhythm": 95 };

  return (
    <div>
      <div className="flex justify-between items-center mb-5">
        <div>
          <div className="text-[19px] font-semibold">Good morning, {fullName.split(" ")[0] || "there"} 👋</div>
          <div className="text-[12.5px] text-faint">System is actively protecting you</div>
        </div>
        <Pill cls="pill-green" label="You are safe" />
      </div>

      {error && (
        <div className="mb-4 text-[12.5px] text-warn bg-[#3a2a05] border border-[#78350f] rounded-lg px-4 py-2.5">
          Backend not reachable ({error}) — showing layout with placeholder data.
        </div>
      )}

      <div className="grid grid-cols-3 gap-4 mb-4">
        <Card label="Identity trust score">
          <div className="flex justify-center"><Gauge value={trustVal} kind="trust" /></div>
          <div className="text-center text-[11px] mt-1" style={{ color: trustColor(trustVal) }}>High trust</div>
        </Card>
        <Card label="Activity risk score">
          <div className="flex justify-center"><Gauge value={riskVal} kind="risk" /></div>
          <div className="text-center text-[11px] mt-1" style={{ color: riskColor(riskVal) }}>Low risk</div>
        </Card>
        <Card label="Current status">
          <div className="mb-2.5"><Pill cls={statusInfo.cls} label={statusInfo.label} /></div>
          <RowLine left="All systems" right="Normal" rightColor="#4ade80" />
          <RowLine left="Re-authentication" right="Not required" rightColor="#4ade80" />
          <RowLine left="Session" right="Active" />
        </Card>
      </div>

      <div className="grid grid-cols-[1.5fr_1fr] gap-4 mb-4">
        <Card label="Trust score trend (last 24 hours)">
          <TrendChart rows={rows} />
        </Card>
        <Card label="Top behavioral factors">
          {Object.entries(factors).map(([label, pct]) => (
            <MiniBar key={label} label={label} pct={pct} color={trustColor(pct)} />
          ))}
        </Card>
      </div>

      <div className="grid grid-cols-[1.5fr_1fr] gap-4">
        <Card label="Recent alerts">
          {alerts && alerts.length > 0 ? (
            alerts.slice(0, 4).map((a) => {
              const sev = (a.severity || "").toUpperCase();
              const color = ["HIGH_RISK", "CRITICAL"].includes(sev) ? "#f87171"
                : ["SUSPICIOUS", "ELEVATED"].includes(sev) ? "#fbbf24" : "#a5b4fc";
              return (
                <RowLine
                  key={a.id}
                  left={a.title || "Alert"}
                  right={new Date(a.created_at).toLocaleString([], { hour: "2-digit", minute: "2-digit", month: "short", day: "numeric" })}
                  rightColor={color}
                />
              );
            })
          ) : (
            <div className="text-good text-[12px] py-2.5">✓ No active alerts</div>
          )}
        </Card>
        <Card label="Quick actions">
          <button className="btn-ghost w-full mb-2 text-left">🔐 Run security check</button>
          <button className="btn-ghost w-full mb-2 text-left">📄 View full report</button>
          <button className="btn-ghost w-full text-left">⚙️ Privacy settings</button>
        </Card>
      </div>
    </div>
  );
}
