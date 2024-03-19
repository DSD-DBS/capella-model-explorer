/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    './src/**/*.{html,js,jsx}'
  ],
  theme: {
    extend: {
      boxShadow: {
        white: '0 0 15px rgba(255, 255, 255, 0.1)',
      }
    }
  },
  plugins: [],
}
