import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
  BarChart, Bar,
} from "recharts";
import { COLORS } from "./theme";

export function TrendChart({ rows = [], height = 210 }) {
  if (!rows.length) {
    return (
      <div className="flex items-center justify-center text-faint text-xs" style={{ height }}>
        No history yet — collecting behavioral data…
      </div>
    );
  }
  const data = rows.map((r) => ({
    time: new Date(r.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    score: r.score,
  }));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={COLORS.good} stopOpacity={0.25} />
            <stop offset="100%" stopColor={COLORS.good} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke={COLORS.border} vertical={false} />
        <XAxis dataKey="time" stroke="#4a5280" fontSize={10} tickLine={false} />
        <YAxis domain={[0, 100]} stroke="#4a5280" fontSize={10} tickLine={false} />
        <Tooltip contentStyle={{ background: "#141733", border: `1px solid ${COLORS.border}`, fontSize: 12 }} />
        <Area type="monotone" dataKey="score" stroke={COLORS.good} fill="url(#trendFill)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function Donut({ segments = [], height = 190, centerText = "" }) {
  return (
    <div className="relative" style={{ height }}>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie data={segments} dataKey="value" innerRadius="68%" outerRadius="100%" startAngle={90} endAngle={-270}>
            {segments.map((s, i) => (
              <Cell key={i} fill={s.color} stroke="#0a0c16" strokeWidth={2} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex items-center justify-center text-xl font-semibold text-text pointer-events-none">
        {centerText}
      </div>
    </div>
  );
}

export function TrendBar({ data = [], height = 170 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid stroke={COLORS.border} vertical={false} />
        <XAxis dataKey="label" stroke="#4a5280" fontSize={10} tickLine={false} />
        <YAxis domain={[0, 100]} stroke="#4a5280" fontSize={10} tickLine={false} />
        <Tooltip contentStyle={{ background: "#141733", border: `1px solid ${COLORS.border}`, fontSize: 12 }} />
        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
          {data.map((d, i) => (
            <Cell key={i} fill={d.value < 30 ? COLORS.good : d.value < 60 ? COLORS.warn : COLORS.bad} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function HorizontalBars({ data = [], height = 200 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 4 }}>
        <CartesianGrid stroke={COLORS.border} horizontal={false} />
        <XAxis type="number" stroke="#4a5280" fontSize={10} tickLine={false} />
        <YAxis type="category" dataKey="label" stroke="#94a3b8" fontSize={11} tickLine={false} width={140} />
        <Tooltip contentStyle={{ background: "#141733", border: `1px solid ${COLORS.border}`, fontSize: 12 }} />
        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
          {data.map((d, i) => (
            <Cell key={i} fill={d.value < 30 ? COLORS.good : d.value < 60 ? COLORS.warn : COLORS.bad} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
