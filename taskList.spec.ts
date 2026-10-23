import { test, expect } from '@playwright/test';

test('Task list full reply and speech chunking', async ({ page }) => {
  // Open the app (assumes dev server is running on localhost:5173)
  await page.goto('http://127.0.0.1:5173');

  // Login – use existing credentials (assuming a test user already logged in via cookies?)
  // For simplicity, we will directly set auth token in localStorage if needed.
  // Replace with actual login steps if the app shows a login page.
  const token = process.env.TEST_AUTH_TOKEN; // should be set externally
  if (token) {
    await page.evaluate(([t]) => localStorage.setItem('authToken', t), [token]);
  }

  // Type the query
  const input = page.getByPlaceholderText(/type a message/i);
  await input.fill('What are my tasks?');
  await input.press('Enter');

  // Wait for reply to appear
  const reply = page.locator('text=Here are your pending tasks:');
  await expect(reply).toBeVisible();

  // Verify that five task lines are rendered
  for (let i = 1; i <= 5; i++) {
    await expect(page.locator(`text=${i}.`).first()).toBeVisible();
  }

  // Capture the speech synthesis utterances via the page's console (we added console.log in useVoice)
  const utterances: string[] = [];
  page.on('console', (msg) => {
    if (msg.text().startsWith('UTTERANCE:')) {
      utterances.push(msg.text().replace('UTTERANCE:', '').trim());
    }
  });

  // The utterances should contain all five tasks (may be split into chunks)
  await page.waitForTimeout(2000); // give time for speech synthesis to queue
  const combined = utterances.join(' ');
  expect(combined).toContain('Prepare slides');
  expect(combined).toContain('Update repo');
  expect(combined).toContain('Schedule meeting');
  expect(combined).toContain('Buy groceries');
  expect(combined).toContain('Read article');

  // Click Replay Voice button (assuming it has aria-label "Replay Voice")
  const replayBtn = page.getByRole('button', { name: /replay voice/i });
  await replayBtn.click();

  // Capture replay utterances (they will be logged the same way)
  const replayUtterances: string[] = [];
  page.on('console', (msg) => {
    if (msg.text().startsWith('UTTERANCE:')) {
      replayUtterances.push(msg.text().replace('UTTERANCE:', '').trim());
    }
  });
  await page.waitForTimeout(2000);
  const replayCombined = replayUtterances.join(' ');
  expect(replayCombined).toBe(combined);
});
