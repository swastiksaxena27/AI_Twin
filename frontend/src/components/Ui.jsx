export function Card({ label, children, className = "" }) {
  return (
    <div className={`card ${className}`}>
      {label && <div className="card-label">{label}</div>}
      {children}
    </div>
  );
}

export function Pill({ cls, label, dot = true }) {
  return (
    <span className={`pill ${cls}`}>
      {dot && "●"} {label}
    </span>
  );
}

export function MiniBar({ label, pct, color }) {
  return (
    <div className="mb-2.5">
      <div className="flex justify-between text-[11.5px] mb-1">
        <span className="text-dim">{label}</span>
        <span style={{ color }}>{pct}%</span>
      </div>
      <div className="h-[5px] bg-border rounded">
        <div className="h-[5px] rounded" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

export function RowLine({ left, right, rightColor }) {
  return (
    <div className="row-line">
      <span className="text-dim">{left}</span>
      <span style={rightColor ? { color: rightColor } : undefined}>{right}</span>
    </div>
  );
}

export function PageHeader({ title, subtitle }) {
  return (
    <div className="mb-4">
      <div className="text-[19px] font-semibold text-text">{title}</div>
      {subtitle && <div className="text-[12.5px] text-faint">{subtitle}</div>}
    </div>
  );
}
