import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        dm: ["var(--font-dm-sans)"],
        inter: ["var(--font-inter)"],
      },
    },
  },
} satisfies Config;
