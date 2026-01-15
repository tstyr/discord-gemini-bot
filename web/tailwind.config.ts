import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'osu-dark': '#111',
        'osu-darker': '#0a0a0a',
        'osu-pink': '#ff66aa',
        'osu-cyan': '#00ffcc',
        'osu-purple': '#aa66ff',
        'osu-card': '#1a1a1a',
        'osu-border': '#333',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'osu-gradient': 'linear-gradient(135deg, #ff66aa 0%, #aa66ff 100%)',
      },
    },
  },
  plugins: [],
}
export default config
