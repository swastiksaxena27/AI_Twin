import { useApp } from "../state/AppContext";
import DashboardPersonal from "./DashboardPersonal";
import DashboardOrg from "./DashboardOrg";

export default function Overview() {
  const { orgMode } = useApp();
  return orgMode ? <DashboardOrg /> : <DashboardPersonal />;
}
