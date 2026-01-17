import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        discord: {
          blurple: "#5865F2",
          green: "#57F287",
          yellow: "#FEE75C",
          fuchsia: "#EB459E",
          red: "#ED4245",
          dark: "#23272A",
          darker: "#1E2124",
        },
        'osu-dark': '#111',
        'osu-darker': '#0a0a0a',
        'osu-pink': '#ff66aa',
        'osu-cyan': '#00ffcc',
        'osu-purple': '#aa66ff',
        'osu-card': '#1a1a1a',
        'osu-border': '#333',
        'osu-gray': '#1a1a1a',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-osu': 'linear-gradient(135deg, #ff66aa 0%, #aa66ff 100%)',
        'gradient-cyan': 'linear-gradient(135deg, #00ffcc 0%, #0099ff 100%)',
        'gradient-purple': 'linear-gradient(135deg, #aa66ff 0%, #ff66aa 100%)',
      },
    },
  },
  plugins: [],
}
export default config
