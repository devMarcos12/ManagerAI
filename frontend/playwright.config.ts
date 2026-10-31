import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests', testMatch: '**/*.spec.ts', fullyParallel: true, workers: 2, retries: 0,
  timeout: 30000, expect: { timeout: 7000 }, reporter: 'list',
  outputDir: process.env.MANAGERAI_TEST_OUTPUT || 'test-results',
  use: { baseURL: 'http://127.0.0.1:5177', viewport: { width: 1440, height: 1000 }, timezoneId: 'America/Sao_Paulo',
    launchOptions: { executablePath: process.env.PLAYWRIGHT_BROWSER_EXECUTABLE_PATH }, trace: 'retain-on-failure' },
  webServer: { command: 'npm run dev -- --port 5177', url: 'http://127.0.0.1:5177', reuseExistingServer: false },
});
