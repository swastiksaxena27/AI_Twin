import { useNavigate } from "react-router-dom";
import { useApp } from "../state/AppContext";
import StepTrack from "../components/StepTrack";

export default function ModeSelect() {
  const navigate = useNavigate();
  const { setOrgMode } = useApp();

  function choose(isOrg) {
    setOrgMode(isOrg);
    navigate("/basic-setup");
  }

  return (
    <div className="min-h-screen bg-radial-fade flex items-center justify-center px-4">
      <div className="w-full max-w-[560px] bg-panel border border-border rounded-[18px] p-9">
        <StepTrack step={1} />
        <div className="text-[19px] font-semibold mb-0.5">Choose your mode</div>
        <div className="text-[12.5px] text-faint mb-6">
          Select how you want to use AI Behavioral Guardian
        </div>

        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => choose(false)}
            className="border border-border rounded-2xl py-6 px-4 text-center hover:border-accent transition-colors"
          >
            <div className="text-[26px] mb-2">👤</div>
            <div className="font-medium mb-1">Personal</div>
            <div className="text-[11.5px] text-faint">
              For individual use — monitor and protect your own device
            </div>
          </button>
          <button
            onClick={() => choose(true)}
            className="border border-border rounded-2xl py-6 px-4 text-center hover:border-accent transition-colors"
          >
            <div className="text-[26px] mb-2">🏢</div>
            <div className="font-medium mb-1">Organization</div>
            <div className="text-[11.5px] text-faint">
              For organizations — monitor and protect multiple users
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
