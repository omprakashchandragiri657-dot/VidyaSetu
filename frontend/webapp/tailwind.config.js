/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'deep-blue': '#1E3A8A',
        'saffron-orange': '#F97316',
        'leaf-green': '#22C55E',
        'light-gray': '#E5E7EB',
        'soft-white': '#F9FAFB',
        'slate-gray': '#475569',
      },
    },
  },
  plugins: [],
}
