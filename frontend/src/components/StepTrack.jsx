export default function StepTrack({ step }) {
  return (
    <div className="flex gap-1.5 mb-7">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className={`flex-1 h-1 rounded ${i <= step ? "bg-accent" : "bg-border"}`} />
      ))}
    </div>
  );
}
