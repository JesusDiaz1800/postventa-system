import { test, expect } from '@playwright/test';

/**
 * E2E Test Suite: Navigation & Core Pages
 * 
 * Tests that critical pages load correctly after login.
 */

const TEST_USER = {
    username: 'jdiaz',
    password: 'adminJDR',
};

test.describe('Core Navigation', () => {
    // Login before each test
    test.beforeEach(async ({ page }) => {
        await page.goto('/');

        // Perform login
        await page.locator('input[name="username"], input[type="text"]').first().fill(TEST_USER.username);
        await page.locator('input[type="password"]').fill(TEST_USER.password);
        await page.locator('button[type="submit"], button:has-text("Iniciar"), button:has-text("Login")').click();

        // Wait for authenticated state
        await expect(page).toHaveURL(/.*dashboard|.*home|.*incidents/i, { timeout: 15000 });
    });

    test('should load incidents page', async ({ page }) => {
        // Navigate to incidents
        await page.click('text=/incidencias/i');

        // Verify incidents page content
        await expect(page.locator('text=/lista.*incidencias|incidencias|gestión/i').first()).toBeVisible({ timeout: 10000 });
    });

    test('should load quality reports page', async ({ page }) => {
        // Navigate to quality reports (may be in a submenu)
        const qualityLink = page.locator('text=/calidad|reportes.*calidad|quality/i').first();
        if (await qualityLink.isVisible()) {
            await qualityLink.click();
            await expect(page.locator('text=/reporte.*calidad|calidad|quality/i').first()).toBeVisible({ timeout: 10000 });
        } else {
            // Skip if quality reports are not visible in navigation
            test.skip();
        }
    });

    test('should load dashboard with statistics', async ({ page }) => {
        // Navigate to dashboard
        await page.click('text=/dashboard|inicio|home/i');

        // Verify dashboard has some statistics or charts
        await expect(page.locator('text=/estadísticas|resumen|total|pendientes/i').first()).toBeVisible({ timeout: 10000 });
    });

    test('should display user information', async ({ page }) => {
        // Look for user info (usually in header/navbar)
        await expect(page.locator(`text=/${TEST_USER.username}/i`).first()).toBeVisible({ timeout: 5000 });
    });
});
