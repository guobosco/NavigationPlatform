import { defineConfig, presetUno, presetIcons, presetAttributify, presetWebFonts } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      warn: true,
    }),
    presetWebFonts({
      fonts: {
        sans: 'Inter:400,600,800',
        mono: 'DM Mono',
      },
    }),
  ],
  shortcuts: [
    ['btn', 'px-4 py-2 rounded inline-block bg-teal-600 text-white cursor-pointer hover:bg-teal-700 disabled:cursor-default disabled:bg-gray-600 disabled:opacity-50'],
    ['icon-btn', 'text-[0.9em] inline-block cursor-pointer select-none opacity-75 transition duration-200 ease-in-out hover:opacity-100 hover:text-teal-600'],
    ['card', 'bg-[var(--card-bg)] rounded-xl shadow-lg transition-transform hover:-translate-y-1 hover:shadow-xl border border-[var(--border-color)]'],
  ],
  theme: {
    colors: {
      primary: 'var(--primary-color)',
      bg: 'var(--bg-primary)',
    }
  },
  rules: [
    // Custom rules if needed
  ]
})
