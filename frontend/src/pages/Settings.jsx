import { useEffect, useState } from "react";
import { useApp } from "../state/AppContext";
import { Card, RowLine } from "../components/Ui";
import { api } from "../api/client";

const TABS = ["General", "Security policies", "Alert rules", "Users & roles", "System info"];

function Toggle({ checked, onChange, label }) {
  return (
    <label className="flex items-center justify-between py-2 cursor-pointer">
      <span className="text-[13px] text-dim">{label}</span>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} className="w-4 h-4 accent-accent" />
    </label>
  );
}

function Slider({ label, value, onChange }) {
  return (
    <div className="mb-4">
      <div className="flex justify-between text-[12.5px] mb-1">
        <span className="text-dim">{label}</span>
        <span className="text-[#a5b4fc]">{value}</span>
      </div>
      <input type="range" min={0} max={100} value={value} onChange={(e) => onChange(Number(e.target.value))} className="w-full accent-accent" />
    </div>
  );
}

// "Connect this device" — trades the browser's short-lived session token for
// a long-lived (30 day) one via /auth/device-token, then hands it to the
// person as a small file to download. The desktop agent picks that file up
// automatically on its next start — no terminal, no typing a password.
function DeviceConnectCard({ userId, username, fullName }) {
  const [status, setStatus] = useState("idle"); // idle | working | done | error
  const [error, setError] = useState(null);

  async function handleConnect() {
    setStatus("working");
    setError(null);
    try {
      const res = await api.connectDevice(); // { access_token, user_id, token_type }
      const pairing = {
        user_id: res.user_id,
        username,
        full_name: fullName,
        access_token: res.access_token,
        issued_for: "behavioral_guardian_agent",
      };
      const blob = new Blob([JSON.stringify(pairing, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "guardian-pairing.json";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setStatus("done");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  return (
    <Card label="Connect this device" className="mb-4">
      <p className="text-[12.5px] text-dim mb-3">
        Download a pairing file and the background agent will link to your account automatically —
        no password typed on this device, ever. The file works for 30 days and only grants the agent
        permission to submit behavioral data as <span className="text-text">{username}</span>.
      </p>
      <button className="btn-primary" onClick={handleConnect} disabled={status === "working"}>
        {status === "working" ? "Generating…" : status === "done" ? "Downloaded ✓ — generate another" : "Download pairing file"}
      </button>
      {status === "done" && (
        <ol className="text-[12px] text-faint mt-3 list-decimal list-inside space-y-1">
          <li>Save <code className="text-dim">guardian-pairing.json</code> to your Downloads folder</li>
          <li>Run the agent — it finds the file automatically and links itself, then deletes it</li>
          <li>Done. Every future run just works, no prompts</li>
        </ol>
      )}
      {status === "error" && <div className="text-warn text-[12.5px] mt-2">{error}</div>}
    </Card>
  );
}

// Maps the snake_case backend SettingsResponse <-> camelCase UI state.
function fromApi(s) {
  return {
    continuousMonitoring: s.continuous_monitoring,
    autoLockCritical: s.auto_lock_critical,
    reauthMediumRisk: s.reauth_medium_risk,
    blockUsbHighRisk: s.block_usb_high_risk,
    highRiskThreshold: s.high_risk_threshold,
    mediumRiskThreshold: s.medium_risk_threshold,
    lowRiskThreshold: s.low_risk_threshold,
    trustSafeThreshold: s.trust_safe_threshold,
  };
}
function toApiKey(key) {
  return {
    continuousMonitoring: "continuous_monitoring",
    autoLockCritical: "auto_lock_critical",
    reauthMediumRisk: "reauth_medium_risk",
    blockUsbHighRisk: "block_usb_high_risk",
    highRiskThreshold: "high_risk_threshold",
    mediumRiskThreshold: "medium_risk_threshold",
    lowRiskThreshold: "low_risk_threshold",
    trustSafeThreshold: "trust_safe_threshold",
  }[key];
}

export default function Settings() {
  const { userId, username, fullName, organization, deviceName, applyProfile } = useApp();
  const [tab, setTab] = useState("General");

  const [name, setName] = useState(fullName);
  const [org, setOrg] = useState(organization);
  const [device, setDevice] = useState(deviceName);
  const [profileSaved, setProfileSaved] = useState(false);

  const [settings, setSettings] = useState(null);
  const [error, setError] = useState(null);
  const [savedKey, setSavedKey] = useState(null);

  useEffect(() => {
    api.getSettings(userId).then((s) => setSettings(fromApi(s))).catch((err) => setError(err.message));
  }, [userId]);

  async function setS(key, val) {
    setSettings((s) => ({ ...s, [key]: val }));
    try {
      const updated = await api.updateSettings(userId, { [toApiKey(key)]: val });
      setSettings(fromApi(updated));
      setSavedKey(key);
      setTimeout(() => setSavedKey(null), 1200);
    } catch (err) {
      setError(err.message);
    }
  }

  async function saveProfile(e) {
    e.preventDefault();
    try {
      const profile = await api.updateUser(userId, { full_name: name, organization: org, device_name: device });
      applyProfile(profile);
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 1500);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <div className="text-[19px] font-semibold mb-0.5">Settings &amp; system configuration</div>
      <div className="text-[12.5px] text-faint mb-4">Configure system behavior and preferences</div>

      {error && (
        <div className="mb-4 text-[12.5px] text-warn bg-[#3a2a05] border border-[#78350f] rounded-lg px-4 py-2.5">
          Backend not reachable ({error}).
        </div>
      )}

      <div className="flex gap-1 mb-4 border-b border-border">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`text-[13px] px-3 py-2 -mb-px border-b-2 ${
              tab === t ? "border-accent text-text" : "border-transparent text-faint hover:text-dim"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "General" && (
        <>
          <DeviceConnectCard userId={userId} username={username} fullName={fullName} />
          <Card label="Profile">
          <form onSubmit={saveProfile}>
            <label className="text-[12px] text-dim block mb-1">Full name</label>
            <input className="input-field mb-3" value={name} onChange={(e) => setName(e.target.value)} />
            <label className="text-[12px] text-dim block mb-1">Organization</label>
            <input className="input-field mb-3" value={org} onChange={(e) => setOrg(e.target.value)} />
            <label className="text-[12px] text-dim block mb-1">Device name</label>
            <input className="input-field mb-3" value={device} onChange={(e) => setDevice(e.target.value)} />
            <button type="submit" className="btn-primary">
              {profileSaved ? "Saved ✓" : "Save profile"}
            </button>
          </form>
          </Card>
        </>
      )}

      {tab === "Security policies" && (
        <>
          {!settings ? (
            <div className="text-faint text-sm">Loading settings…</div>
          ) : (
            <>
              <Card label="Security policies" className="mb-4">
                <Toggle label="Enable continuous monitoring" checked={settings.continuousMonitoring} onChange={(v) => setS("continuousMonitoring", v)} />
                <Toggle label="Auto-lock on critical risk" checked={settings.autoLockCritical} onChange={(v) => setS("autoLockCritical", v)} />
                <Toggle label="Re-authentication on medium risk" checked={settings.reauthMediumRisk} onChange={(v) => setS("reauthMediumRisk", v)} />
                <Toggle label="Block USB on high-risk session" checked={settings.blockUsbHighRisk} onChange={(v) => setS("blockUsbHighRisk", v)} />
              </Card>
              <Card label={`Threshold configuration ${savedKey ? "· saved ✓" : ""}`}>
                <Slider label="High risk threshold" value={settings.highRiskThreshold} onChange={(v) => setS("highRiskThreshold", v)} />
                <Slider label="Medium risk threshold" value={settings.mediumRiskThreshold} onChange={(v) => setS("mediumRiskThreshold", v)} />
                <Slider label="Low risk threshold" value={settings.lowRiskThreshold} onChange={(v) => setS("lowRiskThreshold", v)} />
                <Slider label="Trust safe threshold" value={settings.trustSafeThreshold} onChange={(v) => setS("trustSafeThreshold", v)} />
              </Card>
            </>
          )}
        </>
      )}

      {tab === "Alert rules" && (
        <Card label="Notification channels">
          <Toggle label="Email notifications" checked={true} onChange={() => {}} />
          <Toggle label="Slack notifications" checked={false} onChange={() => {}} />
          <Toggle label="SMS for critical alerts" checked={false} onChange={() => {}} />
        </Card>
      )}

      {tab === "Users & roles" && (
        <Card label="Roles">
          <RowLine left="Admin" right="Full access" rightColor="#a5b4fc" />
          <RowLine left="Analyst" right="View + investigate" rightColor="#a5b4fc" />
          <RowLine left="Viewer" right="Read-only" rightColor="#a5b4fc" />
        </Card>
      )}

      {tab === "System info" && (
        <Card label="System info">
          <RowLine left="Backend" right="● Connected · port 8080" rightColor="#4ade80" />
          <RowLine left="Version" right="v2.4" />
        </Card>
      )}
    </div>
  );
}
