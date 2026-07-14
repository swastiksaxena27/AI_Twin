export const COLORS = {
  good: "#4ade80",
  warn: "#fbbf24",
  bad: "#f87171",
  info: "#60a5fa",
  border: "#1e2240",
};

export function trustColor(value) {
  if (value >= 80) return COLORS.good;
  if (value >= 40) return COLORS.warn;
  return COLORS.bad;
}

export function riskColor(value) {
  if (value < 30) return COLORS.good;
  if (value < 60) return COLORS.warn;
  return COLORS.bad;
}

// Real trust-engine status_level values: NORMAL, ELEVATED, SUSPICIOUS, HIGH_RISK, CRITICAL
export function statusPillInfo(level) {
  const L = (level || "").toUpperCase();
  if (L === "NORMAL") return { cls: "pill-green", label: "Safe" };
  if (L === "ELEVATED") return { cls: "pill-yellow", label: "Watch" };
  if (L === "SUSPICIOUS") return { cls: "pill-yellow", label: "Re-auth" };
  if (L === "HIGH_RISK") return { cls: "pill-red", label: "Restrict" };
  if (L === "CRITICAL") return { cls: "pill-red", label: "Locked" };
  return { cls: "pill-blue", label: level || "Unknown" };
}

// Real alert severity values mirror status_level exactly.
export function severityPillInfo(sev) {
  const S = (sev || "").toUpperCase();
  if (S === "CRITICAL") return { cls: "pill-red", label: "Critical" };
  if (S === "HIGH_RISK") return { cls: "pill-red", label: "High risk" };
  if (S === "SUSPICIOUS") return { cls: "pill-yellow", label: "Suspicious" };
  if (S === "ELEVATED") return { cls: "pill-yellow", label: "Elevated" };
  if (S === "NORMAL") return { cls: "pill-green", label: "Normal" };
  return { cls: "pill-blue", label: sev || "Info" };
}
