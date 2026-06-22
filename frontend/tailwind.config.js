/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      colors: {
        brand: {
          50: "#eff8ff",
          100: "#dbeefe",
          200: "#bfe1fe",
          300: "#93cefd",
          400: "#60b1fa",
          500: "#3b91f6",
          600: "#2473eb",
          700: "#1d5ed8",
          800: "#1e4daf",
          900: "#1e438a",
        },
      },
      boxShadow: {
        glass: "0 1px 2px rgba(15,23,42,0.04), 0 8px 30px rgba(15,23,42,0.06)",
        glow: "0 0 0 1px rgba(59,145,246,0.15), 0 10px 40px rgba(59,145,246,0.18)",
      },
      backgroundImage: {
        "grid-faint":
          "linear-gradient(to right, rgba(15,23,42,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(15,23,42,0.04) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};
