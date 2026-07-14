import { createContext, useContext, useEffect, useState } from "react";
import { clearToken, setToken } from "../api/client";

const AppContext = createContext(null);

function loadPersisted() {
  try {
    const raw = localStorage.getItem("abg_state");
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function AppProvider({ children }) {
  const persisted = loadPersisted();

  const [authed, setAuthed] = useState(persisted.authed || false);
  const [onboarded, setOnboarded] = useState(persisted.onboarded || false);
  const [orgMode, setOrgMode] = useState(persisted.orgMode || false);

  // these mirror the real User row once logged in
  const [userId, setUserId] = useState(persisted.userId || null);
  const [username, setUsername] = useState(persisted.username || "");
  const [fullName, setFullName] = useState(persisted.fullName || "");
  const [organization, setOrganization] = useState(persisted.organization || "");
  const [role, setRole] = useState(persisted.role || "");
  const [deviceName, setDeviceName] = useState(persisted.deviceName || "");
  const [isOrgAdmin, setIsOrgAdmin] = useState(persisted.isOrgAdmin || false);

  useEffect(() => {
    localStorage.setItem(
      "abg_state",
      JSON.stringify({
        authed, onboarded, orgMode, userId, username, fullName,
        organization, role, deviceName, isOrgAdmin,
      })
    );
  }, [authed, onboarded, orgMode, userId, username, fullName, organization, role, deviceName, isOrgAdmin]);

  /** Called after a successful /auth/login or /auth/register response.
   *  Accepts the full AuthResponse so it can also stash the bearer token. */
  function applyAuthUser(user, accessToken) {
    setUserId(user.id);
    setUsername(user.username);
    setFullName(user.full_name || user.username);
    setOrganization(user.organization || "");
    setRole(user.role || "");
    setDeviceName(user.device_name || "");
    setIsOrgAdmin(!!user.is_org_admin);
    setAuthed(true);
    if (accessToken) setToken(accessToken);
  }

  /** Called after Basic Setup PATCHes the profile — keep context in sync. */
  function applyProfile(profile) {
    setFullName(profile.full_name || profile.username);
    setOrganization(profile.organization || "");
    setRole(profile.role || "");
    setDeviceName(profile.device_name || "");
  }

  function signOut() {
    localStorage.removeItem("abg_state");
    clearToken();
    setAuthed(false);
    setOnboarded(false);
    setUserId(null);
  }

  const value = {
    authed, setAuthed,
    onboarded, setOnboarded,
    orgMode, setOrgMode,
    userId,
    username,
    fullName, setFullName,
    organization, setOrganization,
    role, setRole,
    deviceName, setDeviceName,
    isOrgAdmin,
    applyAuthUser,
    applyProfile,
    signOut,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used inside AppProvider");
  return ctx;
}
