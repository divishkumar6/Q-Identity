/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    'text-gold-400', 'text-gold-500', 'bg-gold-500', 'bg-gold-500/10', 'bg-gold-500/15', 'border-gold-500/20', 'border-gold-500/40',
    'text-blue-400', 'text-blue-500', 'bg-blue-500', 'bg-blue-500/10', 'bg-blue-500/15', 'border-blue-500/20', 'border-blue-500/40',
    'text-emerald-400', 'text-emerald-500', 'bg-emerald-500', 'bg-emerald-500/10', 'bg-emerald-500/15', 'border-emerald-500/20', 'border-emerald-500/40',
    'text-red-400', 'text-red-500', 'bg-red-500', 'bg-red-500/10', 'bg-red-500/15', 'border-red-500/20',
    'text-purple-400',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#0a0e1a',
          900: '#0f1629',
          800: '#151d38',
          700: '#1c2647',
          600: '#243056',
        },
        gold: {
          50: '#fdf8ed',
          100: '#f9edcf',
          200: '#f3d99e',
          300: '#ecc36d',
          400: '#e5ab3d',
          500: '#d49422',
          600: '#b87518',
          700: '#965616',
          800: '#7c4519',
          900: '#683a19',
        },
        charcoal: {
          900: '#1a1a2e',
          800: '#22223a',
          700: '#2a2a44',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
