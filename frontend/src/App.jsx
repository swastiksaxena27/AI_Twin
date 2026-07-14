import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppProvider, useApp } from "./state/AppContext";
import { getToken } from "./api/client";

import Login from "./pages/Login";
import ModeSelect from "./pages/ModeSelect";
import BasicSetup from "./pages/BasicSetup";
import BehaviorLearning from "./pages/BehaviorLearning";
import AppShell from "./pages/AppShell";
import Overview from "./pages/Overview";
import UserDetail from "./pages/UserDetail";
import LiveMonitor from "./pages/LiveMonitor";
import AlertsCenter from "./pages/AlertsCenter";
import RiskAnalytics from "./pages/RiskAnalytics";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";

function RootRedirect() {
  const { authed, onboarded } = useApp();
  if (!authed || !getToken()) return <Navigate to="/login" replace />;
  if (!onboarded) return <Navigate to="/mode-select" replace />;
  return <Navigate to="/app/overview" replace />;
}

/** Guards the /app/* routes — bounces to /login if there's no session token,
 *  even if stale `authed` state survived in localStorage from a previous run. */
function RequireAuth({ children }) {
  const { authed } = useApp();
  if (!authed || !getToken()) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<Login />} />
          <Route path="/mode-select" element={<ModeSelect />} />
          <Route path="/basic-setup" element={<BasicSetup />} />
          <Route path="/behavior-learning" element={<BehaviorLearning />} />

          <Route path="/app" element={<RequireAuth><AppShell /></RequireAuth>}>
            <Route path="overview" element={<Overview />} />
            <Route path="user/:id" element={<UserDetail />} />
            <Route path="live-monitor" element={<LiveMonitor />} />
            <Route path="alerts" element={<AlertsCenter />} />
            <Route path="risk-analytics" element={<RiskAnalytics />} />
            <Route path="reports" element={<Reports />} />
            <Route path="settings" element={<Settings />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
