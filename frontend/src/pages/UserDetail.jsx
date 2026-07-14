import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useUserData } from "../api/useUserData";
import { api } from "../api/client";
import Gauge from "../components/Gauge";
import { TrendChart } from "../components/Charts";
import { Card, Pill, MiniBar, RowLine } from "../components/Ui";
import { trustColor, statusPillInfo } from "../components/theme";

// Small inline hook so the risk gauge uses the real /risk/{id} endpoint
// (TrustResponse has no activity_risk field — that lives on RiskResponse).
function useRisk(userId) {
  const [risk, setRisk] = useState(null);
  useEffect(() => {
    let cancelled = false;
    api.getRisk(userId).then((r) => { if (!cancelled) setRisk(r.activity_risk); }).catch(() => {});
    return () => { cancelled = true; };
  }, [userId]);
  return risk;
}

// Fetches the real profile (name/role/device) for the drilled-into user.
function useProfile(userId) {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    let cancelled = false;
    api.getUser(userId)
      .then((p) => { if (!cancelled) setProfile(p); })
      .catch((err) => { if (!cancelled) setError(err.message); });
    return () => { cancelled = true; };
  }, [userId]);
  return { profile, error };
}

export default function UserDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const userId = Number(id);

  const { profile, error: profileError } = useProfile(userId);
  const person = profile
    ? { id: userId, name: profile.full_name || profile.username, role: profile.role || "—", device: profile.device_name || "—" }
    : { id: userId, name: `User ${userId}`, role: "—", device: "—" };

  const { trust, history, error } = useUserData(userId, { poll: 15000 });
  const riskVal = useRisk(userId) ?? 0;

  const trustVal = trust?.identity_trust ?? 0;
  const status = trust?.status_level ?? "UNKNOWN";
  const statusInfo = statusPillInfo(status);
  const rows = history?.trust_history ?? [];

  const initials = person.name.split(" ").slice(0, 2).map((w) => w[0]).join("");
  const indicators = { "Typing pattern": 80, "Mouse usage": 87, "Working hours": 75, "Device consistency": 95 };

  return (
    <div>
      <button onClick={() => navigate("/app/overview")} className="btn-ghost mb-4">
        ← Back to users
      </button>

      <div className="flex items-center gap-3 mb-5">
        <div className="w-[46px] h-[46px] rounded-full bg-[#1e1b4b] border border-accentDim flex items-center justify-center text-[15px] text-[#a5b4fc]">
          {initials}
        </div>
        <div>
          <div className="text-[19px] font-semibold">{person.name}</div>
          <div className="text-[12.5px] text-faint">{person.role} · {person.device} · Last seen recently</div>
        </div>
      </div>

      {(error || profileError) && (
        <div className="mb-4 text-[12.5px] text-warn bg-[#3a2a05] border border-[#78350f] rounded-lg px-4 py-2.5">
          Backend not reachable ({error || profileError}) — showing layout with placeholder data.
        </div>
      )}

      <div className="grid grid-cols-3 gap-4 mb-4">
        <Card label="Current trust score">
          <div className="flex justify-center"><Gauge value={trustVal} kind="trust" /></div>
        </Card>
        <Card label="Current risk score">
          <div className="flex justify-center"><Gauge value={riskVal} kind="risk" /></div>
        </Card>
        <Card label="Status">
          <div className="mb-2.5"><Pill cls={statusInfo.cls} label={statusInfo.label} /></div>
          <RowLine left="Identity trust" right={trustVal.toFixed(0)} rightColor={trustColor(trustVal)} />
          <RowLine left="Device" right={person.device} />
        </Card>
      </div>

      <div className="grid grid-cols-[1.6fr_1fr] gap-4">
        <Card label="Risk timeline (last 24 hours)">
          <TrendChart rows={rows} />
        </Card>
        <Card label="Behavioral indicators">
          {Object.entries(indicators).map(([label, pct]) => (
            <MiniBar key={label} label={label} pct={pct} color={trustColor(pct)} />
          ))}
        </Card>
      </div>
    </div>
  );
}
