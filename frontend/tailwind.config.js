/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}"
  ],
  prefix: "",
  theme: {
    extend: {
      screens: {
        sm: "576px",
        md: "850px",
        lg: "1100px",
        xl: "1200px",
        "2xl": "1400px"
      },
      colors: {
        primary: "#3B86C6",
        bg: {
          DEFAULT: "#F3F4F8"
        },
        text: {
          secondary: "#6A6E80"
        }
      }
    }
  },
  plugins: []
};
