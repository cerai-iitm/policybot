/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class", // Enables dark mode via the .dark class
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--bg)",
        "background-dark": "var(--bg-dark)",
        "background-light": "var(--bg-light)",
        foreground: "var(--text)",
        "foreground-muted": "var(--text-muted)",
        highlight: "var(--highlight)",
        outline: "var(--border)",
        "outline-muted": "var(--border-muted)",
        primary: "var(--primary)",
        secondary: "var(--secondary)",
        danger: "var(--danger)",
        warning: "var(--warning)",
        success: "var(--success)",
        info: "var(--info)",
      },
    },
  },
  plugins: [],
};
