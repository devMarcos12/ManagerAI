import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests', testMatch: '**/*.real.ts', workers: 1, retries: 0, timeout: 180000,
  expect: { timeout: 90000 }, reporter: 'list', outputDir: process.env.MANAGERAI_TEST_OUTPUT || 'test-results',
  use: { baseURL: process.env.MANAGERAI_WEB_URL || 'http://127.0.0.1:5173', viewport: { width: 1440, height: 1000 },
    launchOptions: { executablePath: process.env.PLAYWRIGHT_BROWSER_EXECUTABLE_PATH }, trace: 'off' },
});
