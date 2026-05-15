/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
    "./features/**/*.{js,jsx}",
    "./hooks/**/*.{js,jsx}",
    "./lib/**/*.{js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "#070A12",
        panel: "rgba(255,255,255,0.08)",
        borderSoft: "rgba(255,255,255,0.14)",
        cyanGlow: "#59F6E8",
        limeGlow: "#B6F36B",
        coralGlow: "#FF7A7A"
      },
      boxShadow: {
        glass: "0 24px 80px rgba(0, 0, 0, 0.35)",
        glow: "0 0 42px rgba(89, 246, 232, 0.18)"
      }
    }
  },
  plugins: []
};

