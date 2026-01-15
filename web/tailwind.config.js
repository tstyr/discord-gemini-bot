/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'osu-pink': '#ff66aa',
        'osu-cyan': '#00ffcc',
        'osu-purple': '#aa66ff',
        'osu-darker': '#0a0a0a',
        'osu-dark': '#111111',
        'osu-card': '#1a1a1a',
        'osu-border': '#333333',
      },
      backgroundImage: {
        'osu-gradient': 'linear-gradient(135deg, #ff66aa 0%, #aa66ff 100%)',
        'osu-gradient-cyan': 'linear-gradient(135deg, #00ffcc 0%, #66aaff 100%)',
      },
      fontFamily: {
        'exo': ['Exo 2', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      }
    },
  },
  plugins: [],
}