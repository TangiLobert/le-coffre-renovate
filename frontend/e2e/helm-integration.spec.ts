import { test, expect, type Page } from '@playwright/test'

/**
 * Helm Integration E2E Test
 *
 * Validates the full lifecycle of Le Coffre deployed via Helm on Minikube:
 *   1. Setup wizard: create vault with Shamir shares
 *   2. Store the generated shares
 *   3. Create admin account & complete setup
 *   4. Login with admin credentials
 *   5. Unlock the vault using the stored shares
 *   6. Create a password entry
 *   7. Read/reveal the created password
 *
 * This test runs as a single sequential flow because each step depends
 * on state produced by the previous one (shares, auth session, etc.).
 */

const ADMIN_EMAIL = 'admin@ci-test.com'
const ADMIN_PASSWORD = 'CiTestP@ssw0rd!'
const ADMIN_DISPLAY_NAME = 'CI Admin'

const TEST_PASSWORD_NAME = 'CI Test Password'
const TEST_PASSWORD_VALUE = 'S3cretP@ss!'
const TEST_PASSWORD_LOGIN = 'ci-user@example.com'
const TEST_PASSWORD_URL = 'https://example.com'
const TEST_PASSWORD_FOLDER = 'CI Tests'

// Use 2 shares / threshold 2 for simplicity in CI
const SHARES_COUNT = 2
const THRESHOLD = 2

test.describe('Helm Integration - Full Lifecycle', () => {
  // Shared state across serial tests
  let storedShares: string[] = []

  test.describe.configure({ mode: 'serial' })

  test('Setup wizard: create vault, store shares, create admin', async ({ page }) => {
    // Navigate to the app — should redirect to /setup since vault is not initialized
    await page.goto('/')
    await expect(page).toHaveURL(/\/setup/, { timeout: 30000 })

    // ── Step 1: Welcome ────────────────────────────────────────
    await expect(page.getByText('Welcome onboard!')).toBeVisible({ timeout: 10000 })
    await page.getByRole('button', { name: 'Start setup' }).click()

    // ── Step 2: Generate Master Key ────────────────────────────
    await expect(page.getByText("Let's generate the master key")).toBeVisible({ timeout: 10000 })

    // Set shares and threshold to 2/2 for CI simplicity
    const sharesInput = page.locator('#shares')
    const thresholdInput = page.locator('#threshold')

    await sharesInput.click()
    await sharesInput.fill(String(SHARES_COUNT))
    await thresholdInput.click()
    await thresholdInput.fill(String(THRESHOLD))

    // Generate the master key
    await page.getByRole('button', { name: 'Generate shares of the master key' }).click()

    // Wait for the shares modal to appear
    await expect(page.getByText('Shares of the master key')).toBeVisible({ timeout: 30000 })

    // Extract share secrets from the modal.
    // Toggle visibility on each PrimeVue Password field so .inputValue() returns the real secret.
    storedShares = []
    for (let i = 0; i < SHARES_COUNT; i++) {
      const shareInput = page.locator(`#share-secret-${i}`)
      const toggleButton = shareInput
        .locator('xpath=..')
        .locator('button[type="button"], .p-password-toggle-mask-icon')
        .first()
      // Always click to toggle visibility — the button is expected to be present
      await toggleButton.click()
      await expect(shareInput).not.toHaveValue('', { timeout: 5000 })
      const shareValue = await shareInput.inputValue()
      storedShares.push(shareValue)
    }
    expect(storedShares).toHaveLength(SHARES_COUNT)

    // Confirm shares have been stored
    await page.locator('#storedSharesCheckbox').click()
    await page.getByRole('button', { name: 'Continue' }).click()

    // ── Step 3: Create Admin Account ───────────────────────────
    await expect(page.getByText('Create Admin Account')).toBeVisible({ timeout: 10000 })

    await page.locator('#email').fill(ADMIN_EMAIL)

    // PrimeVue Password fields: fill the underlying <input> inside the component
    const passwordInput = page.locator('#password')
    await passwordInput.fill(ADMIN_PASSWORD)

    const confirmPasswordInput = page.locator('#confirm_password')
    await confirmPasswordInput.fill(ADMIN_PASSWORD)

    await page.locator('#display_name').fill(ADMIN_DISPLAY_NAME)

    // Submit the admin account form
    await page.getByRole('button', { name: 'Create admin account' }).click()

    // ── Step 4: Setup Done ─────────────────────────────────────
    await expect(page.getByText('Setup is done!')).toBeVisible({ timeout: 30000 })
  })

  test('Login with admin credentials', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible({ timeout: 15000 })

    await page.locator('#email').fill(ADMIN_EMAIL)
    await page.locator('#password').fill(ADMIN_PASSWORD)
    await page.getByRole('button', { name: 'Login', exact: true }).click()

    // After login, vault is locked — expect unlock modal or password manager
    await expect(page.getByText('Unlock Vault').or(page.getByText('Password Manager'))).toBeVisible(
      { timeout: 15000 },
    )
  })

  test('Unlock the vault with shares', async ({ page }) => {
    await loginAsAdmin(page)

    // The unlock modal should appear since vault is locked
    await expect(page.getByText('Unlock Vault')).toBeVisible({ timeout: 15000 })

    // Fill in the first share (already has one input field)
    await page.locator('#share-0').fill(storedShares[0])

    // Add and fill remaining shares
    for (let i = 1; i < storedShares.length; i++) {
      await page.getByRole('button', { name: 'Add Share' }).click()
      await page.locator(`#share-${i}`).fill(storedShares[i])
    }

    // Submit shares to unlock
    await page.getByRole('button', { name: 'Submit Shares' }).click()

    // Vault should unlock — Password Manager becomes visible
    await expect(page.getByText('Password Manager')).toBeVisible({ timeout: 30000 })
  })

  test('Create a password', async ({ page }) => {
    await loginAsAdmin(page)
    await unlockVaultIfNeeded(page)

    await expect(page.getByText('Password Manager')).toBeVisible({ timeout: 15000 })

    // Open the "New Password" modal
    await page.getByRole('button', { name: 'New Password' }).click()
    await expect(page.getByText('Create New Password')).toBeVisible({ timeout: 10000 })

    // Fill in the password form
    await page.locator('#password-name').fill(TEST_PASSWORD_NAME)
    await page.locator('#password-value').fill(TEST_PASSWORD_VALUE)
    await page.locator('#password-login').fill(TEST_PASSWORD_LOGIN)
    await page.locator('#password-url').fill(TEST_PASSWORD_URL)
    await page.locator('#password-folder').fill(TEST_PASSWORD_FOLDER)

    // Submit
    await page.getByRole('button', { name: 'Create' }).click()

    // Wait for the password to appear in the list
    await expect(page.getByText(TEST_PASSWORD_NAME)).toBeVisible({ timeout: 15000 })
  })

  test('Read/reveal the created password', async ({ page }) => {
    await loginAsAdmin(page)
    await unlockVaultIfNeeded(page)

    await expect(page.getByText('Password Manager')).toBeVisible({ timeout: 15000 })

    // Expand the folder containing our password
    await page.locator('div').filter({ hasText: TEST_PASSWORD_FOLDER }).first().click()

    // Wait for the password card to be visible
    await expect(page.getByText(TEST_PASSWORD_NAME)).toBeVisible({ timeout: 10000 })

    // Click the "Show password" (eye) button on the password card
    const showButton = page.getByRole('button', { name: 'Show password' })
    await showButton.click()

    // After revealing, the password value should be displayed (not bullets)
    const passwordCode = page.locator('code').first()
    await expect(passwordCode).toHaveText(TEST_PASSWORD_VALUE, { timeout: 10000 })
  })

  test('Lock the vault', async ({ page }) => {
    await loginAsAdmin(page)
    await unlockVaultIfNeeded(page)

    await expect(page.getByText('Password Manager')).toBeVisible({ timeout: 15000 })

    // Open the main menu to find the lock option
    await page.getByRole('button', { name: 'Menu' }).click()

    // Look for lock button — it might be in a menu or settings
    // Common patterns: "Lock", "Lock Vault", or similar
    const lockButton = page.getByRole('button', { name: /lock/i })
    await lockButton.click()

    // After locking, the unlock modal should appear
    await expect(page.getByText('Unlock Vault')).toBeVisible({ timeout: 15000 })
  })

  test('Unlock with first share only (partial)', async ({ page }) => {
    await loginAsAdmin(page)

    // The vault is already locked from the previous test
    await expect(page.getByText('Unlock Vault')).toBeVisible({ timeout: 15000 })

    // Fill in only the first share
    await page.locator('#share-0').fill(storedShares[0])

    // Try to submit with only one share (should fail or show error since threshold is 2)
    const submitButton = page.getByRole('button', { name: 'Submit Shares' })
    await submitButton.click()

    // Expect either an error message or the unlock modal to remain (not unlocked)
    // We should still see the unlock modal or an error indicating more shares are needed
    await expect(
      page.getByText('Unlock Vault').or(page.getByText(/more shares|insufficient|need/i)),
    ).toBeVisible({ timeout: 10000 })
  })

  test('Unlock with remaining shares (complete unlock)', async ({ page }) => {
    // Stay on the same page with the unlock modal still showing
    // The first share should still be filled from the previous test

    // Add the second share
    await page.getByRole('button', { name: 'Add Share' }).click()
    await page.locator('#share-1').fill(storedShares[1])

    // Now submit with both shares
    await page.getByRole('button', { name: 'Submit Shares' }).click()

    // Vault should unlock — Password Manager becomes visible
    await expect(page.getByText('Password Manager')).toBeVisible({ timeout: 30000 })
  })

  // ── Helper functions ─────────────────────────────────────────

  async function loginAsAdmin(page: Page) {
    await page.goto('/login')
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible({ timeout: 15000 })

    await page.locator('#email').fill(ADMIN_EMAIL)
    await page.locator('#password').fill(ADMIN_PASSWORD)
    await page.getByRole('button', { name: 'Login', exact: true }).click()

    // Wait for either unlock modal or password manager
    await expect(page.getByText('Unlock Vault').or(page.getByText('Password Manager'))).toBeVisible(
      { timeout: 15000 },
    )
  }

  async function unlockVaultIfNeeded(page: Page) {
    // Try to detect if unlock is needed by checking the page state.
    // The unlockVault modal blocks interaction, so try to fill shares and submit.
    const unlockHeader = page.getByText('Unlock Vault')
    // Give a short timeout — if it's not visible the vault is already unlocked
    const needsUnlock = await unlockHeader
      .waitFor({ state: 'visible', timeout: 3000 })
      .then(() => true)
      .catch(() => false)
    if (!needsUnlock) return

    await page.locator('#share-0').fill(storedShares[0])
    for (let i = 1; i < storedShares.length; i++) {
      await page.getByRole('button', { name: 'Add Share' }).click()
      await page.locator(`#share-${i}`).fill(storedShares[i])
    }

    await page.getByRole('button', { name: 'Submit Shares' }).click()
    await expect(page.getByText('Password Manager')).toBeVisible({ timeout: 30000 })
  }
})
