/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx,css}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1e40af',
        secondary: '#f472b6',
      },
    },
  },
  plugins: [],
}
