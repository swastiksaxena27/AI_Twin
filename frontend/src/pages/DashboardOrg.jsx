import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../state/AppContext";
import { api } from "../api/client";
import { useUserData } from "../api/useUserData";
import { TrendChart, Donut } from "../components/Charts";
import { Card, RowLine } from "../components/Ui";
import { COLORS } from "../components/theme";

function useRoster(organization) {
  const [users, setUsers] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const profiles = await api.getUsers(organization || undefined);
        if (!cancelled) {
          setUsers(
            profiles.map((p) => ({
              id: p.id,
              name: p.full_name || p.username,
              role: p.role || "—",
              trust: p.identity_trust,
              risk: p.activity_risk,
              status: p.status_level,
            }))
          );
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    }
    load();
    const interval = setInterval(load, 15000);
    return () => { cancelled = true; clearInterval(interval); };
  }, [organization]);

  return { users, error };
}

export default function DashboardOrg() {
  const navigate = useNavigate();
  const { organization, userId } = useApp();
  const { users, error } = useRoster(organization);
  const { history } = useUserData(userId);

  if (error && !users) {
    return (
      <div className="text-[12.5px] text-warn bg-[#3a2a05] border border-[#78350f] rounded-lg px-4 py-2.5">
        Backend not reachable ({error}).
      </div>
    );
  }
  if (!users) return <div className="text-faint text-sm">Loading organization overview…</div>;
  if (users.length === 0) {
    return (
      <div className="text-[12.5px] text-faint bg-panel border border-border rounded-lg px-4 py-3">
        No other users found in your organization yet. As teammates sign in with the same organization name, they'll show up here.
      </div>
    );
  }

  const highRisk = users.filter((u) => u.risk > 60);
  const avgTrust = users.reduce((s, u) => s + u.trust, 0) / users.length;

  const trustHigh = users.filter((u) => u.trust >= 80).length;
  const trustMid = users.filter((u) => u.trust >= 40 && u.trust < 80).length;
  const trustLow = users.filter((u) => u.trust < 40).length;

  const riskLow = users.filter((u) => u.risk < 30).length;
  const riskMid = users.filter((u) => u.risk >= 30 && u.risk < 60).length;
  const riskHigh = users.filter((u) => u.risk >= 60).length;

  const rows = history?.trust_history ?? [];

  return (
    <div>
      <div className="text-[19px] font-semibold mb-0.5">Overview dashboard</div>
      <div className="text-[12.5px] text-faint mb-5">
        Real-time status and trust overview across your organization
      </div>

      <div className="grid grid-cols-4 gap-4 mb-4">
        <Card label="Total users"><div className="text-2xl font-semibold">{users.length}</div></Card>
        <Card label="High risk users"><div className="text-2xl font-semibold">{highRisk.length}</div></Card>
        <Card label="Critical alerts"><div className="text-2xl font-semibold">{highRisk.length}</div></Card>
        <Card label="Avg trust score"><div className="text-2xl font-semibold">{avgTrust.toFixed(0)}</div></Card>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <Card label="Identity trust distribution">
          <Donut
            segments={[
              { value: trustHigh, color: COLORS.good },
              { value: trustMid, color: COLORS.warn },
              { value: trustLow, color: COLORS.bad },
            ]}
            centerText={users.length}
          />
        </Card>
        <Card label="Activity risk distribution">
          <Donut
            segments={[
              { value: riskLow, color: COLORS.good },
              { value: riskMid, color: COLORS.warn },
              { value: riskHigh, color: COLORS.bad },
            ]}
            centerText={users.length}
          />
        </Card>
        <Card label="Top alerts">
          {[...users].sort((a, b) => b.risk - a.risk).slice(0, 4).map((u) => (
            <RowLine
              key={u.id}
              left={u.name}
              right={`${u.risk.toFixed(0)} risk`}
              rightColor={u.risk > 60 ? COLORS.bad : u.risk > 30 ? COLORS.warn : COLORS.good}
            />
          ))}
        </Card>
      </div>

      <div className="grid grid-cols-[1.6fr_1fr] gap-4 mb-4">
        <Card label="Trust score over time (system average)">
          <TrendChart rows={rows} />
        </Card>
        <Card label="Recent activities">
          {users.slice(0, 5).map((u) => (
            <RowLine key={u.id} left={u.name} right={u.role} />
          ))}
        </Card>
      </div>

      <Card label="Users — click to drill into individual monitoring">
        <div className="grid grid-cols-[2fr_2fr_1fr_1fr_1fr_0.8fr] text-[10.5px] text-faint uppercase mb-2">
          <div>User</div><div>Role</div><div>Trust</div><div>Risk</div><div>Status</div><div></div>
        </div>
        {users.map((u) => (
          <div key={u.id} className="grid grid-cols-[2fr_2fr_1fr_1fr_1fr_0.8fr] items-center py-1.5 border-b border-border last:border-none text-[12.5px]">
            <div>{u.name}</div>
            <div className="text-faint text-[12px]">{u.role}</div>
            <div style={{ color: u.trust >= 80 ? COLORS.good : u.trust >= 40 ? COLORS.warn : COLORS.bad }}>{u.trust.toFixed(0)}</div>
            <div style={{ color: u.risk > 60 ? COLORS.bad : u.risk > 30 ? COLORS.warn : COLORS.good }}>{u.risk.toFixed(0)}</div>
            <div>
              <span className={`pill ${u.trust >= 80 ? "pill-green" : u.trust >= 40 ? "pill-yellow" : "pill-red"}`}>
                {u.status}
              </span>
            </div>
            <button className="btn-ghost text-[12px] py-1 px-3" onClick={() => navigate(`/app/user/${u.id}`)}>
              View
            </button>
          </div>
        ))}
      </Card>
    </div>
  );
}
