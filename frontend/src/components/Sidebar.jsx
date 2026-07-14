import { NavLink, useNavigate } from "react-router-dom";
import { useApp } from "../state/AppContext";

const NAV_ITEMS = [
  { to: "/app/overview", label: "Overview", icon: "🏠" },
  { to: "/app/live-monitor", label: "Live Monitor", icon: "📡" },
  { to: "/app/alerts", label: "Alerts", icon: "🚨" },
  { to: "/app/risk-analytics", label: "Risk Analytics", icon: "📊" },
  { to: "/app/reports", label: "Reports", icon: "📄" },
  { to: "/app/settings", label: "Settings", icon: "⚙️" },
];

export default function Sidebar() {
  const { fullName, orgMode, signOut } = useApp();
  const navigate = useNavigate();

  function handleSignOut() {
    signOut();
    navigate("/login");
  }

  return (
    <aside className="w-[230px] shrink-0 bg-[#07080f] border-r border-border min-h-screen flex flex-col px-3 py-4">
      <div className="flex items-center gap-2 px-1 pb-4">
        <div className="w-8 h-8 rounded-[9px] bg-gradient-to-br from-accent to-accentDim flex items-center justify-center text-base">
          🛡️
        </div>
        <div>
          <div className="text-[14.5px] font-semibold text-text leading-tight">AI Behavioral Guardian</div>
          <div className="text-[9.5px] text-faint tracking-wide">CONTINUOUS TRUST · INTELLIGENT PROTECTION</div>
        </div>
      </div>
      <hr className="border-border mb-2" />

      <nav className="flex flex-col gap-1">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-2.5 text-[13.5px] px-3 py-2 rounded-lg transition-colors ${
                isActive
                  ? "bg-gradient-to-r from-accentDim to-[#1e1b4b] text-[#c7d2fe] border-l-2 border-accent font-medium"
                  : "text-dim hover:bg-raised hover:text-text"
              }`
            }
          >
            <span>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="flex-1" />

      <hr className="border-border mb-3" />
      <div className="text-[11px] text-faint px-1 mb-3">
        <div className="flex items-center gap-1.5 mb-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-good inline-block" />
          Backend · port 8080
        </div>
        <div>
          {fullName || "Guest"} · {orgMode ? "Organization" : "Personal"} mode
        </div>
      </div>
      <button onClick={handleSignOut} className="btn-ghost text-left">
        ⏏ Sign out
      </button>
    </aside>
  );
}
