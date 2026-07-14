import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../state/AppContext";
import StepTrack from "../components/StepTrack";

const FACTORS = ["Typing pattern", "Mouse movement", "Application usage", "Activity rhythm"];

export default function BehaviorLearning() {
  const navigate = useNavigate();
  const { setOnboarded } = useApp();
  const [progress] = useState(45);

  function finish() {
    setOnboarded(true);
    navigate("/app/overview");
  }

  return (
    <div className="min-h-screen bg-radial-fade flex items-center justify-center px-4">
      <div className="w-full max-w-[420px] bg-panel border border-border rounded-[18px] p-9">
        <StepTrack step={3} />
        <div className="text-[19px] font-semibold mb-0.5">Building your digital twin</div>
        <div className="text-[12.5px] text-faint mb-5">
          Learning your normal behavior patterns. Stay active, use your device normally.
        </div>

        <div className="h-2 bg-border rounded-full mb-2 overflow-hidden">
          <div className="h-2 bg-accent rounded-full" style={{ width: `${progress}%` }} />
        </div>
        <div className="flex justify-between mb-5">
          <span className="text-[12px] text-[#a5b4fc] font-semibold">{progress}% complete</span>
          <span className="text-[11.5px] text-faint">Estimated time remaining: 3–7 days</span>
        </div>

        <div className="grid grid-cols-2 gap-2 mb-5">
          {FACTORS.map((f) => (
            <div key={f} className="card py-2.5 px-3.5">
              <div className="text-[12px] text-dim">{f}</div>
              <div className="text-[11px] text-good">Learning…</div>
            </div>
          ))}
        </div>

        <button onClick={finish} className="btn-primary w-full">
          Continue to dashboard
        </button>
      </div>
    </div>
  );
}
