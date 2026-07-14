/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0a0c16",
        panel: "#0f1120",
        raised: "#141733",
        border: "#1e2240",
        text: "#e2e8f0",
        dim: "#94a3b8",
        faint: "#4a5280",
        accent: "#6d5ef9",
        accentDim: "#4338ca",
        good: "#4ade80",
        warn: "#fbbf24",
        bad: "#f87171",
        info: "#60a5fa",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        xl2: "14px",
      },
      backgroundImage: {
        "radial-fade": "radial-gradient(circle at 15% 0%, #161a3a 0%, #0a0c16 45%)",
      },
    },
  },
  plugins: [],
}
