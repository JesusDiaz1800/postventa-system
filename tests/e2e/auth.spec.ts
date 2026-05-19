import { test, expect } from '@playwright/test';

/**
 * E2E Test Suite: Authentication
 * 
 * Tests the login flow for Postventa System.
 * These tests run against the local dev server.
 */

const TEST_USER = {
    username: 'jdiaz',
    password: 'adminJDR',
};

test.describe('Authentication', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to the login page
        await page.goto('/');
    });

    test('should display login form', async ({ page }) => {
        // Verify login form is visible
        await expect(page.locator('input[name="username"], input[type="text"]').first()).toBeVisible();
        await expect(page.locator('input[type="password"]')).toBeVisible();
        await expect(page.locator('button[type="submit"], button:has-text("Iniciar"), button:has-text("Login")')).toBeVisible();
    });

    test('should show error for invalid credentials', async ({ page }) => {
        // Fill in wrong credentials
        await page.locator('input[name="username"], input[type="text"]').first().fill('wronguser');
        await page.locator('input[type="password"]').fill('wrongpass');

        // Click login button
        await page.locator('button[type="submit"], button:has-text("Iniciar"), button:has-text("Login")').click();

        // Wait for error (check multiple possible indicators)
        // Could be: error text, still on login page, or toast notification
        await page.waitForTimeout(3000); // Wait for response

        // Verify we're still on login page (login failed)
        const stillOnLogin = await page.locator('input[type="password"]').isVisible();
        expect(stillOnLogin).toBeTruthy();
    });

    test('should login successfully with valid credentials', async ({ page }) => {
        // Fill in valid credentials
        await page.locator('input[name="username"], input[type="text"]').first().fill(TEST_USER.username);
        await page.locator('input[type="password"]').fill(TEST_USER.password);

        // Click login button
        await page.locator('button[type="submit"], button:has-text("Iniciar"), button:has-text("Login")').click();

        // Wait for navigation (app redirects to /reports after login)
        await expect(page).toHaveURL(/.*dashboard|.*home|.*incidents|.*reports/i, { timeout: 15000 });

        // Verify we're logged in (any authenticated content should be visible)
        await expect(page.locator('nav, [role="navigation"], header').first()).toBeVisible({ timeout: 10000 });
    });

    test('should persist login across page refresh', async ({ page }) => {
        // Login first
        await page.locator('input[name="username"], input[type="text"]').first().fill(TEST_USER.username);
        await page.locator('input[type="password"]').fill(TEST_USER.password);
        await page.locator('button[type="submit"], button:has-text("Iniciar"), button:has-text("Login")').click();

        // Wait for authenticated page
        await expect(page).toHaveURL(/.*dashboard|.*home|.*incidents|.*reports/i, { timeout: 15000 });

        // Refresh the page
        await page.reload();

        // Should still be logged in (not redirected to login)
        await expect(page).not.toHaveURL(/.*login/i, { timeout: 5000 });
    });
});
