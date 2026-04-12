import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2F4DBA",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
        serif: ['"Source Serif 4"', 'serif'],
        dm: ["var(--font-dm-sans)"],
        inter: ["var(--font-inter)"],
      },
    },
  },
  darkMode: "class",
 
} satisfies Config;
