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
        background: "#070907",
        panel: "#101610",
        borderSoft: "rgba(255,255,255,0.14)",
        cyanGlow: "#8FE8C5",
        limeGlow: "#BEEA75",
        coralGlow: "#F6A66D",
        zenCream: "#F5F1E8",
        zenSage: "#8FE8C5",
        zenGold: "#F6C779"
      },
      boxShadow: {
        glass: "0 24px 80px rgba(0, 0, 0, 0.35)",
        glow: "0 0 42px rgba(89, 246, 232, 0.18)"
      }
    }
  },
  plugins: []
};
