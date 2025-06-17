module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        'poppins': ['Poppins', 'sans-serif'],
      },
      colors: {
        'primary-blue': '#0097DC',
        'light-blue': '#EFF9FF',
        'blue-50': '#EFF9FF',
        'blue-100': '#E2F2FC',
        'blue-600': '#0097DC',
      },
      backgroundImage: {
        'gradient-blue': 'linear-gradient(180deg, #EFF9FF 0%, #E2F2FC 99%)',
      }
    },
  },
  plugins: [],
} 