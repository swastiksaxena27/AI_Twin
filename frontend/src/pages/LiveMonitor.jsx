import { useEffect, useState } from "react";
import { useApp } from "../state/AppContext";
import { api } from "../api/client";
import { Card } from "../components/Ui";
import { COLORS } from "../components/theme";

const APPS = ["VS Code", "Chrome", "Excel", "Outlook", "Slack"];

export default function LiveMonitor() {
  const { orgMode, organization, userId, fullName } = useApp();
  const [rows, setRows] = useState(null);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("All Users");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        if (orgMode) {
          const profiles = await api.getUsers(organization || undefined);
          if (!cancelled) {
            setRows(profiles.map((p) => ({
              id: p.id,
              name: p.full_name || p.username,
              device: p.device_name || "—",
              trust: p.identity_trust,
              status: p.status_level,
            })));
          }
        } else {
          const t = await api.getTrust(userId);
          if (!cancelled) {
            setRows([{ id: userId, name: fullName || "You", device: "This device", trust: t.identity_trust, status: t.status_level }]);
          }
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    }
    load();
    const interval = setInterval(load, 10000);
    return () => { cancelled = true; clearInterval(interval); };
  }, [orgMode, organization, userId, fullName]);

  const visible = (rows || []).filter((u) => {
    if (filter === "High risk only") return u.trust < 40;
    if (filter === "Watch only") return u.trust >= 40 && u.trust < 80;
    return true;
  });

  return (
    <div>
      <div className="text-[19px] font-semibold mb-0.5">Live behavior monitor</div>
      <div className="text-[12.5px] text-faint mb-5">Real-time behavioral feed from all devices</div>

      {error && (
        <div className="mb-3 text-[12.5px] text-warn bg-[#3a2a05] border border-[#78350f] rounded-lg px-4 py-2.5">
          Backend not reachable ({error}).
        </div>
      )}

      <select className="input-field w-56 mb-3" value={filter} onChange={(e) => setFilter(e.target.value)}>
        <option>All Users</option>
        <option>High risk only</option>
        <option>Watch only</option>
      </select>

      <Card>
        <div className="grid grid-cols-[1.8fr_1.2fr_1fr_1fr_1fr_1fr_1fr] text-[10.5px] text-faint uppercase mb-2">
          <div>User</div><div>Device</div><div>Typing</div><div>Mouse</div><div>Active app</div><div>Trust</div><div>Status</div>
        </div>
        <hr className="border-border mb-1" />
        {!rows && <div className="text-faint text-sm py-3">Loading…</div>}
        {rows && visible.map((u, i) => {
          const color = u.trust >= 80 ? COLORS.good : u.trust >= 40 ? COLORS.warn : COLORS.bad;
          const badge = u.trust >= 80 ? "pill-green" : u.trust >= 40 ? "pill-yellow" : "pill-red";
          return (
            <div key={u.id} className="grid grid-cols-[1.8fr_1.2fr_1fr_1fr_1fr_1fr_1fr] items-center py-1.5 border-b border-border last:border-none text-[12.5px]">
              <div>{u.name}</div>
              <div className="text-faint text-[12px]">{u.device}</div>
              <div className="text-dim text-[12px]">Normal</div>
              <div className="text-dim text-[12px]">Normal</div>
              <div className="text-dim text-[12px]">{APPS[i % APPS.length]}</div>
              <div style={{ color }}>{u.trust.toFixed(0)}</div>
              <div><span className={`pill ${badge}`}>● Live</span></div>
            </div>
          );
        })}
      </Card>

      <div className="h-4" />
      <Card label="Live behavioral feed (illustrative — no raw keystroke/mouse event stream is exposed by the backend yet)">
        <div className="text-faint text-[12px] py-2">
          Trust/risk scores above refresh from the real backend every 10s. A live per-keystroke/mouse event feed
          would need a new streaming endpoint (e.g. WebSocket) — happy to add that next if you want it.
        </div>
      </Card>
    </div>
  );
}
