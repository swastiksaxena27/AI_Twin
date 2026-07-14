import { useState } from "react";
import { useApp } from "../state/AppContext";
import { useUserData } from "../api/useUserData";
import { Card } from "../components/Ui";
import { severityPillInfo } from "../components/theme";

export default function AlertsCenter() {
  const { userId } = useApp();
  const { alerts, error } = useUserData(userId, { poll: 15000 });
  const [severityFilter, setSeverityFilter] = useState("All");
  const [readFilter, setReadFilter] = useState("All");

  const list = alerts || [];
  const critical = list.filter((a) => a.severity === "CRITICAL");
  const highRisk = list.filter((a) => a.severity === "HIGH_RISK");
  const unread = list.filter((a) => !a.is_read);

  const visible = list.filter((a) => {
    if (severityFilter !== "All") {
      const map = { Critical: "CRITICAL", "High risk": "HIGH_RISK", Suspicious: "SUSPICIOUS", Elevated: "ELEVATED", Normal: "NORMAL" };
      if (a.severity !== map[severityFilter]) return false;
    }
    if (readFilter === "Unread" && a.is_read) return false;
    if (readFilter === "Read" && !a.is_read) return false;
    return true;
  });

  return (
    <div>
      <div className="text-[19px] font-semibold mb-0.5">Alerts &amp; incidents center</div>
      <div className="text-[12.5px] text-faint mb-5">All alerts in one place</div>

      <div className="grid grid-cols-4 gap-4 mb-4">
        <Card label="Total alerts"><div className="text-2xl font-semibold">{list.length}</div></Card>
        <Card label="Critical"><div className="text-2xl font-semibold">{critical.length}</div></Card>
        <Card label="High risk"><div className="text-2xl font-semibold">{highRisk.length}</div></Card>
        <Card label="Unread"><div className="text-2xl font-semibold">{unread.length}</div></Card>
      </div>

      <div className="flex gap-3 mb-3">
        <select className="input-field w-48" value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
          {["All", "Critical", "High risk", "Suspicious", "Elevated", "Normal"].map((o) => <option key={o}>{o}</option>)}
        </select>
        <select className="input-field w-40" value={readFilter} onChange={(e) => setReadFilter(e.target.value)}>
          {["All", "Unread", "Read"].map((o) => <option key={o}>{o}</option>)}
        </select>
      </div>

      <Card label="All alerts — latest first">
        {error && (
          <div className="text-[12.5px] text-warn">Backend not reachable ({error}).</div>
        )}
        {!error && visible.length === 0 && (
          <div className="text-good text-[13px] py-4 text-center">✓ No alerts for this user</div>
        )}
        {!error && visible.length > 0 && (
          <>
            <div className="grid grid-cols-[1.2fr_2fr_2.2fr_1fr_0.8fr] text-[10.5px] text-faint uppercase mb-2">
              <div>Time</div><div>Alert</div><div>Detail</div><div>Severity</div><div>Read</div>
            </div>
            <hr className="border-border mb-1" />
            {visible.map((a) => {
              const sev = severityPillInfo(a.severity);
              return (
                <div key={a.id} className="grid grid-cols-[1.2fr_2fr_2.2fr_1fr_0.8fr] items-start py-2 border-b border-border last:border-none text-[12.5px]">
                  <div className="text-faint text-[12px]">{new Date(a.created_at).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</div>
                  <div>{a.title}</div>
                  <div className="text-dim text-[12px]">{a.message}</div>
                  <div><span className={`pill ${sev.cls}`}>{sev.label}</span></div>
                  <div className="text-faint text-[12px]">{a.is_read ? "✓" : "●"}</div>
                </div>
              );
            })}
          </>
        )}
      </Card>
    </div>
  );
}
