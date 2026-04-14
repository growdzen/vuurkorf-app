import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#fdf4f0",
          100: "#fae5d8",
          200: "#f5c8b0",
          300: "#eda07c",
          400: "#e4724a",
          500: "#d94f28",
          600: "#c0391d",
          700: "#9f2c19",
          800: "#82261b",
          900: "#6b231a",
        },
        fire: {
          DEFAULT: "#d94f28",
          dark: "#9f2c19",
          light: "#f5c8b0",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
