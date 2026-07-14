import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../state/AppContext";
import { api } from "../api/client";

// A profile counts as "already set up" if BasicSetup has actually been
// filled in before — used to skip re-onboarding on a second device/browser
// instead of trusting only this browser's local onboarded flag.
function looksOnboarded(user) {
  return Boolean(user.full_name && user.device_name);
}

export default function Login() {
  const navigate = useNavigate();
  const { applyAuthUser, setOnboarded } = useApp();
  const [mode, setMode] = useState("signin"); // "signin" | "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function afterAuth(res) {
    applyAuthUser(res.user, res.access_token);
    if (looksOnboarded(res.user)) {
      setOnboarded(true);
      navigate("/app/overview");
    } else {
      navigate("/mode-select");
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!email || !password) {
      setError("Enter both an email/username and a password.");
      return;
    }
    setBusy(true);
    try {
      if (mode === "signup") {
        const username = email.includes("@") ? email.split("@")[0] : email;
        const reg = await api.register({ username, password, email: email.includes("@") ? email : undefined });
        if (!reg.success) {
          setError(reg.message || "Could not create your account.");
          return;
        }
        afterAuth(reg);
        return;
      }

      const res = await api.login({ identifier: email, password });
      if (!res.success) {
        // Deliberately vague, same as the backend: this could mean "wrong
        // password" OR "no account with this identifier" — the backend
        // never distinguishes the two (that's intentional, it stops anyone
        // from probing which emails have accounts). So we point at "Create
        // one" rather than silently registering a new account on their behalf,
        // which used to cause a login typo to quietly spawn an unrelated account.
        setError(res.message || "Could not sign in. Wrong password, or no account yet — use \"Create account\" below.");
        return;
      }
      afterAuth(res);
    } catch (err) {
      setError(err.message || "Could not reach the server.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-radial-fade flex items-center justify-center px-4">
      <form onSubmit={handleSubmit} className="auth-shell w-full max-w-[420px] bg-panel border border-border rounded-[18px] p-9">
        <div className="w-[46px] h-[46px] rounded-xl bg-gradient-to-br from-accent to-accentDim flex items-center justify-center text-2xl mb-3.5">
          🛡️
        </div>
        <div className="text-xl font-semibold mb-0.5">{mode === "signin" ? "Welcome back" : "Create your account"}</div>
        <div className="text-[12.5px] text-faint mb-6">
          {mode === "signin" ? "Sign in to AI Behavioral Guardian" : "Set up a new AI Behavioral Guardian account"}
        </div>

        <label className="text-[12.5px] text-dim block mb-1">Email / Username</label>
        <input
          className="input-field mb-4"
          placeholder="you@company.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="username"
        />

        <label className="text-[12.5px] text-dim block mb-1">Password</label>
        <input
          type="password"
          className="input-field mb-3"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete={mode === "signin" ? "current-password" : "new-password"}
        />

        {mode === "signin" && (
          <div className="flex justify-end items-center mb-5 text-[12px]">
            <span className="text-faint cursor-not-allowed" title="Not available yet — contact your admin to reset a password">
              Forgot password?
            </span>
          </div>
        )}
        {mode === "signup" && <div className="mb-5" />}

        {error && (
          <div className="text-[12px] text-[#f87171] mb-4 bg-[#3b0a0a] border border-[#7f1d1d] rounded-lg px-3 py-2">
            {error}
          </div>
        )}

        <button type="submit" className="btn-primary w-full" disabled={busy}>
          {busy ? (mode === "signin" ? "Signing in…" : "Creating account…") : mode === "signin" ? "Sign in" : "Create account"}
        </button>

        <hr className="border-border my-5" />
        <div className="text-center text-[12px] text-faint">
          {mode === "signin" ? (
            <>
              New here?{" "}
              <button
                type="button"
                className="text-[#a5b4fc] hover:underline"
                onClick={() => { setMode("signup"); setError(""); }}
              >
                Create an account
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button
                type="button"
                className="text-[#a5b4fc] hover:underline"
                onClick={() => { setMode("signin"); setError(""); }}
              >
                Sign in instead
              </button>
            </>
          )}
        </div>
      </form>
    </div>
  );
}
