import { useEffect, useState } from "react";
import { api } from "../api/client";

/**
 * Pulls trust + risk + alerts + history for a single user.
 * Returns { trust, risk, alerts, history, loading, error }.
 * On backend failure, error is set and the others remain null so the
 * page can show a clear "backend unreachable" state instead of crashing.
 */
export function useUserData(userId, { poll = 0 } = {}) {
  const [state, setState] = useState({ trust: null, risk: null, alerts: null, history: null, loading: true, error: null });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [trust, risk, alerts, history] = await Promise.all([
          api.getTrust(userId),
          api.getRisk(userId),
          api.getAlerts(userId),
          api.getHistory(userId),
        ]);
        if (!cancelled) setState({ trust, risk, alerts, history, loading: false, error: null });
      } catch (err) {
        if (!cancelled) setState((s) => ({ ...s, loading: false, error: err.message }));
      }
    }

    load();
    let interval;
    if (poll > 0) interval = setInterval(load, poll);
    return () => {
      cancelled = true;
      if (interval) clearInterval(interval);
    };
  }, [userId, poll]);

  return state;
}
