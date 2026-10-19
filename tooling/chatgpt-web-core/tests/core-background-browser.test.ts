import { expect, test } from "bun:test";
import { chromium } from "playwright-core";
import { defaultChromeExecutable } from "../src/config";
import { managedChromeLaunchOptions, minimizeManagedPage } from "../src/adapters/chatgpt-web/browser-worker";

// Opt-in native-window smoke: no login profile, network navigation, or model request.
test.skipIf(process.env.CORE_BROWSER_SMOKE !== "1")("headed inference pages remain minimized across navigation and typing", async () => {
  const config = { chromeExecutablePath: defaultChromeExecutable(), headed: true, startMinimized: true };
  const browser = await chromium.launch(managedChromeLaunchOptions(config));
  try {
    const context = await browser.newContext();
    for (let index = 0; index < 2; index++) {
      const page = await context.newPage();
      await minimizeManagedPage(page, config);
      await page.goto('data:text/html,<label>Composer<textarea></textarea></label><button>Model</button>');
      await page.getByRole("textbox").fill("Local fixture only");
      await page.getByRole("button", { name: "Model" }).click();
      const session = await context.newCDPSession(page);
      try {
        const state = await session.send("Browser.getWindowForTarget");
        expect(state.bounds.windowState).toBe("minimized");
        console.log(JSON.stringify({ page: index + 1, headed: true, windowState: state.bounds.windowState }));
      } finally { await session.detach(); }
      await page.close();
    }
  } finally { await browser.close(); }
}, 20000);
