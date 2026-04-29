/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pe: {
          teal: {
            50: '#E6FFFA',
            100: '#B2F5EA',
            200: '#81E6D9',
            300: '#4FD1C5',
            400: '#38B2AC',
            500: '#319795',
            600: '#2C7A7B',
            700: '#285E61',
            800: '#234E52',
            900: '#1D4044',
          },
          blue: {
            500: '#0EA5E9',
            700: '#026AA2',
          },
          gray: {
            50: '#F9FAFB',
            100: '#F2F4F7',
            200: '#E2E8F0',
            300: '#CBD5E1',
            500: '#6B7280',
            600: '#4B5563',
            700: '#344054',
          },
          bg: {
            primary: '#FFFFFF',
            secondary: '#F5F9FF',
            tertiary: '#F1F5F9',
          },
          text: {
            primary: '#000000',
            secondary: '#5A5A5A',
            tertiary: '#9CA3AF',
          },
          success: '#22C55E',
          error: '#EF4444',
          warning: '#FEC601',
          info: '#1890FF',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      borderRadius: {
        'pe-sm': '4px',
        'pe-md': '6px',
        'pe-lg': '8px',
      },
    },
  },
  plugins: [],
}
