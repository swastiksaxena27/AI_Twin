import { RadialBarChart, RadialBar, PolarAngleAxis } from "recharts";
import { trustColor, riskColor } from "./theme";

/**
 * kind = "trust" (higher is better) | "risk" (lower is better)
 */
export default function Gauge({ value = 0, kind = "trust", size = 170 }) {
  const color = kind === "trust" ? trustColor(value) : riskColor(value);
  const data = [{ value, fill: color }];

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <RadialBarChart
        width={size}
        height={size}
        cx="50%"
        cy="50%"
        innerRadius="72%"
        outerRadius="100%"
        barSize={14}
        data={data}
        startAngle={90}
        endAngle={-270}
      >
        <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
        <RadialBar background={{ fill: "#1e2240" }} dataKey="value" cornerRadius={8} />
      </RadialBarChart>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-semibold" style={{ color }}>
          {Math.round(value)}
        </span>
        <span className="text-[10px] text-faint">/100</span>
      </div>
    </div>
  );
}
