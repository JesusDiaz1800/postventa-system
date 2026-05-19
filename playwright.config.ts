import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for Postventa System E2E Tests
 * 
 * Run tests with: npx playwright test
 * Run with UI:    npx playwright test --ui
 * Debug mode:     npx playwright test --debug
 */

export default defineConfig({
    testDir: './tests/e2e',

    /* Run tests in parallel */
    fullyParallel: true,

    /* Fail the build on CI if you accidentally left test.only in the source code */
    forbidOnly: !!process.env.CI,

    /* Retry on failure */
    retries: process.env.CI ? 2 : 0,

    /* Reporter to use */
    reporter: [
        ['html', { outputFolder: 'tests/e2e/playwright-report' }],
        ['list'],
    ],

    /* Shared settings for all projects */
    use: {
        /* Base URL for the app - adjust to your local IP if needed */
        baseURL: 'https://localhost:5173',

        /* Collect trace on failure */
        trace: 'on-first-retry',

        /* Screenshot on failure */
        screenshot: 'only-on-failure',

        /* Accept self-signed certificates (required for local HTTPS) */
        ignoreHTTPSErrors: true,

        /* Increase timeout for slower operations */
        actionTimeout: 10000,
    },

    /* Configure projects for different browsers */
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
    ],

    /* Timeout for each test */
    timeout: 60000,

    /* Output directory for test artifacts */
    outputDir: 'tests/e2e/test-results',
});
