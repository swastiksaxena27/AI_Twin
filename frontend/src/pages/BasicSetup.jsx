import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../state/AppContext";
import StepTrack from "../components/StepTrack";
import { api } from "../api/client";

const TIMEZONES = [
  "(GMT+05:30) Asia/Kolkata",
  "(GMT+00:00) UTC",
  "(GMT-05:00) US/Eastern",
  "(GMT+01:00) Europe/Berlin",
];

export default function BasicSetup() {
  const navigate = useNavigate();
  const { userId, fullName, organization, orgMode, role, applyProfile } = useApp();

  const [name, setName] = useState(fullName);
  const [org, setOrg] = useState(organization);
  const [timezone, setTimezone] = useState(TIMEZONES[0]);
  const [device, setDevice] = useState("My Laptop");
  const [purpose, setPurpose] = useState(role || "Work");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const profile = await api.updateUser(userId, {
        full_name: name || fullName,
        organization: orgMode ? org : "",
        role: purpose,
        device_name: device,
      });
      applyProfile(profile);
      navigate("/behavior-learning");
    } catch (err) {
      setError(err.message || "Could not save your details — try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-radial-fade flex items-center justify-center px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-[420px] bg-panel border border-border rounded-[18px] p-9">
        <StepTrack step={2} />
        <div className="text-[19px] font-semibold mb-0.5">Basic setup</div>
        <div className="text-[12.5px] text-faint mb-5">Fill in a few details to get started</div>

        <label className="text-[12.5px] text-dim block mb-1">Full Name</label>
        <input className="input-field mb-3" value={name} onChange={(e) => setName(e.target.value)} />

        {orgMode && (
          <>
            <label className="text-[12.5px] text-dim block mb-1">Organization</label>
            <input className="input-field mb-3" value={org} onChange={(e) => setOrg(e.target.value)} />
          </>
        )}

        <label className="text-[12.5px] text-dim block mb-1">Time Zone</label>
        <select className="input-field mb-3" value={timezone} onChange={(e) => setTimezone(e.target.value)}>
          {TIMEZONES.map((tz) => (
            <option key={tz}>{tz}</option>
          ))}
        </select>

        <label className="text-[12.5px] text-dim block mb-1">Device Name</label>
        <input className="input-field mb-3" value={device} onChange={(e) => setDevice(e.target.value)} />

        <label className="text-[12.5px] text-dim block mb-1">Purpose</label>
        <input className="input-field mb-4" value={purpose} onChange={(e) => setPurpose(e.target.value)} />

        {error && (
          <div className="text-[12px] text-[#f87171] mb-4 bg-[#3b0a0a] border border-[#7f1d1d] rounded-lg px-3 py-2">
            {error}
          </div>
        )}

        <button type="submit" className="btn-primary w-full" disabled={busy}>
          {busy ? "Saving…" : "Continue"}
        </button>
      </form>
    </div>
  );
}
