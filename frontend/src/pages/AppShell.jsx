import { Outlet, Navigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { useApp } from "../state/AppContext";

export default function AppShell() {
  const { authed, onboarded } = useApp();

  if (!authed) return <Navigate to="/login" replace />;
  if (!onboarded) return <Navigate to="/mode-select" replace />;

  return (
    <div className="flex min-h-screen bg-radial-fade">
      <Sidebar />
      <main className="flex-1 px-8 py-7 max-w-[1300px]">
        <Outlet />
      </main>
    </div>
  );
}
