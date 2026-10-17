/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: 'var(--surface)',
        panel: 'var(--panel)',
        ink: 'var(--ink)',
        'ink-soft': 'var(--ink-soft)',
        matched: 'var(--matched)',
        missing: 'var(--missing)',
        rule: 'var(--rule)',
        'rule-subtle': 'var(--rule-subtle)',
      },
      fontFamily: {
        sans: ['"Schibsted Grotesk"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'],
      },
      borderRadius: {
        none: '0px',
        sm: '2px',
        md: '8px',
      }
    },
  },
  plugins: [],
}
