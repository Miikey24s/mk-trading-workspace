import { expect, test } from "bun:test";
import { chromium, type Page } from "playwright-core";
import { mkdtempSync, rmSync, writeFileSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { defaultChromeExecutable } from "../src/config";
import { ChatGptBrowserWorker, managedChromeLaunchOptions, managedChromeContext } from "../src/adapters/chatgpt-web/browser-worker";
import { ChatGptMarkdownBuffer, type ChatGptMarkdownSegment } from "../src/adapters/chatgpt-web/markdown";

test("current renderer binds only the new answer when its toolbar shares a column with the private prompt", async () => {
  const browser = await chromium.launch(managedChromeLaunchOptions({ chromeExecutablePath: defaultChromeExecutable(), headed: false }));
  try {
    const page = await browser.newPage();
    const worker = Object.create(ChatGptBrowserWorker.prototype) as {
      bindCurrentAssistantResponse(page: Page, baseline: { initialTurnIdentities: string[]; currentAssistantActionCount: number }): Promise<{ locator: any } | undefined>;
      responseDomSnapshot(locator: any): Promise<{ visibleText: string; markdownSegments: ChatGptMarkdownSegment[] }>;
    };
    for (const answer of ["Chào bạn. Mình là Mentor.", "Dòng đầu.\n\nDòng cuối.", "Một câu trả lời dài. ".repeat(300)]) {
      await page.setContent(`<style>main { margin: 20px auto; width: 700px } .actions { display:flex; height:30px } .actions button { width:30px }</style>
        <main><div><div><p>PRIVATE INSTRUCTIONS must never be delivered</p><button aria-label="Copy"></button></div>
        <div><div><p id="answer"></p></div></div></div><div class="actions"><span><button aria-label="Copy"></button></span><span><button aria-label="Read aloud"></button></span><button></button><button></button></div></main>`);
      await page.locator('#answer').evaluate((node, text) => { node.textContent = text; }, answer);
      const binding = await worker.bindCurrentAssistantResponse(page, { initialTurnIdentities: [], currentAssistantActionCount: 0 });
      expect(binding).toBeDefined();
      const snapshot = await worker.responseDomSnapshot(binding!.locator);
      expect(snapshot.visibleText.replace(/\s+/g, " ")).toBe(answer.trim().replace(/\s+/g, " "));
      const buffer = new ChatGptMarkdownBuffer();
      buffer.observe(snapshot.markdownSegments);
      expect(buffer.finish().markdown).not.toContain("PRIVATE INSTRUCTIONS");
    }
    await page.setContent('<main><p>Only a user bubble</p><button aria-label="Copy"></button></main>');
    expect(await worker.bindCurrentAssistantResponse(page, { initialTurnIdentities: [], currentAssistantActionCount: 0 })).toBeUndefined();
    await page.setContent(readFileSync(new URL('./fixtures/chatgpt-shared-turn-group.html', import.meta.url), 'utf8'));
    const shared = await worker.responseDomSnapshot(page.locator('[data-turn-key]'));
    expect(shared.visibleText).toBe('REPLAY READY');
    const buffer = new ChatGptMarkdownBuffer();
    buffer.observe(shared.markdownSegments);
    expect(buffer.finish().markdown).toBe('REPLAY READY');
  } finally { await browser.close(); }
}, 20000);

test("headless product context restores login storage and native identity and accepts real clicks", async () => {
  const directory = mkdtempSync(join(tmpdir(), "core-hidden-test-"));
  const server = Bun.serve({ hostname: "127.0.0.1", port: 0, fetch: () => new Response('<textarea></textarea><button onclick="document.body.dataset.clicked=1">Send</button>', { headers: { 'content-type': 'text/html' } }) });
  const origin = `http://127.0.0.1:${server.port}`;
  const storage = join(directory, "state.json");
  writeFileSync(storage, JSON.stringify({ cookies: [], origins: [{ origin, localStorage: [{ name: 'fixture', value: 'restored' }] }] }));
  const options = managedChromeLaunchOptions({ chromeExecutablePath: defaultChromeExecutable(), headed: false });
  expect(options.headless).toBe(true);
  const browser = await chromium.launch(options);
  const context = await managedChromeContext(browser, { storageStatePath: storage, useNativeUserAgent: true });
  try {
    for (let index = 0; index < 2; index++) {
      const page = await context.newPage();
      await page.goto(origin);
      expect(await page.evaluate(() => localStorage.getItem('fixture'))).toBe('restored');
      expect(await page.evaluate(() => navigator.userAgent)).not.toContain('HeadlessChrome');
      await page.locator('textarea').fill('Synthetic input');
      await page.getByRole('button', { name: 'Send' }).click();
      expect(await page.locator('body').getAttribute('data-clicked')).toBe('1');
      await page.close();
    }
  } finally {
    await browser.close();
    await server.stop(true);
    rmSync(directory, { recursive: true, force: true });
  }
}, 30000);
