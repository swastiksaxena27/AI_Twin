import { useState } from "react";
import { useApp } from "../state/AppContext";
import { useUserData } from "../api/useUserData";
import { Card } from "../components/Ui";

export default function Reports() {
  const { userId } = useApp();
  const { history } = useUserData(userId);
  const rows = history?.trust_history ?? [];

  const [reportType, setReportType] = useState("Trust & risk summary");
  const [format, setFormat] = useState("PDF");

  return (
    <div>
      <div className="text-[19px] font-semibold mb-0.5">Reports &amp; history</div>
      <div className="text-[12.5px] text-faint mb-4">View analytics and activity history</div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <Card label="Data points"><div className="text-2xl font-semibold">{rows.length}</div></Card>
        <Card label="Report period"><div className="text-2xl font-semibold">7 days</div></Card>
        <Card label="Export format"><div className="text-2xl font-semibold">CSV / PDF</div></Card>
      </div>

      <Card label="Generate report" className="mb-4">
        <div className="grid grid-cols-2 gap-3 mb-3">
          <select className="input-field" value={reportType} onChange={(e) => setReportType(e.target.value)}>
            <option>Trust &amp; risk summary</option>
            <option>Alerts log</option>
            <option>Behavioral analytics</option>
          </select>
          <select className="input-field" value={format} onChange={(e) => setFormat(e.target.value)}>
            <option>PDF</option>
            <option>CSV</option>
            <option>JSON</option>
          </select>
        </div>
        <button className="btn-primary">Generate report</button>
      </Card>

      <Card label="Raw trust history">
        {rows.length === 0 ? (
          <div className="text-faint text-[12px] py-4 text-center">No history available yet</div>
        ) : (
          <div className="max-h-72 overflow-y-auto">
            <div className="grid grid-cols-3 text-[10.5px] text-faint uppercase mb-2">
              <div>Created at</div><div>Score</div><div>Label</div>
            </div>
            {rows.map((r, i) => (
              <div key={i} className="grid grid-cols-3 text-[12.5px] py-1.5 border-b border-border last:border-none">
                <div className="text-dim">{new Date(r.created_at).toLocaleString()}</div>
                <div>{r.score}</div>
                <div className="text-faint">{r.label}</div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
