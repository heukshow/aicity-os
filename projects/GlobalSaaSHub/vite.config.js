import fs from 'node:fs'
import path from 'node:path'
import { privateOpsBuildGuard } from './scripts/private_ops_build_guard.mjs'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

function coshumaBrandIdentity() {
  return {
    name: 'coshuma-brand-identity',
    apply: 'build',
    closeBundle() {
      const dist = path.resolve('dist')
      if (!fs.existsSync(dist)) return
      const favicon = '<link rel="icon" href="/brand/coshuma-favicon.svg" type="image/svg+xml" />'
      const runtime = '<script defer src="/brand/brand-runtime.js"></script>'
      const walk = (dir) => {
        for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
          const full = path.join(dir, entry.name)
          if (entry.isDirectory()) walk(full)
          else if (entry.isFile() && entry.name.endsWith('.html')) {
            let html = fs.readFileSync(full, 'utf8')
            if (!html.includes('/brand/coshuma-favicon.svg') && html.includes('</head>')) html = html.replace('</head>', `  ${favicon}\n</head>`)
            if (!html.includes('/brand/brand-runtime.js') && html.includes('</head>')) html = html.replace('</head>', `  ${runtime}\n</head>`)
            fs.writeFileSync(full, html)
          }
        }
      }
      walk(dist)
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  plugins: [react(), tailwindcss(), privateOpsBuildGuard(), coshumaBrandIdentity()],
  build: {
    rollupOptions: {
      output: {
        entryFileNames: `assets/[name]-${Date.now()}.js`,
        chunkFileNames: `assets/[name]-${Date.now()}.js`,
        assetFileNames: `assets/[name]-${Date.now()}[extname]`
      }
    }
  }
})
