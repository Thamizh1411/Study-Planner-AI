/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,jsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          50: '#f6f6f7',
          100: '#e1e1e4',
          200: '#c5c5cb',
          300: '#9e9ea7',
          400: '#757581',
          500: '#5c5c68',
          600: '#474751',
          700: '#3a3a42',
          800: '#242429',
          900: '#17171a',
          950: '#0f0f12',
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
