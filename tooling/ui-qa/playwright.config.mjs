import { defineConfig } from '@playwright/test'
import { browserPath } from './qa.mjs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const kit = path.dirname(fileURLToPath(import.meta.url))
const run = process.env.TW_UI_QA_RUN_DIR
if (!run || !path.resolve(run).startsWith(path.join(kit, 'artifacts') + path.sep)) {
  throw new Error('Run via qa.mjs smoke to allocate an isolated evidence directory')
}

export default defineConfig({
  testDir: path.join(kit, 'smoke'),
  timeout: 15000, expect: { timeout: 5000 }, globalTimeout: 50000,
  workers: 1, retries: 0, forbidOnly: true,
  outputDir: path.join(run, 'test-results'),
  reporter: [['list'], ['json', { outputFile: path.join(run, 'results.json') }]],
  use: { browserName: 'chromium', headless: true, locale: 'vi-VN', timezoneId: 'Asia/Ho_Chi_Minh',
    serviceWorkers: 'block', reducedMotion: 'reduce', trace: 'retain-on-failure',
    screenshot: 'only-on-failure', video: 'off',
    launchOptions: { executablePath: browserPath() } },
  projects: [360, 768, 1440].map(width => ({ name: `width-${width}`, use: { viewport: { width, height: 900 } } })),
})
