import { afterAll, expect, test } from "bun:test";
import { mkdtempSync, rmSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { initializeCore } from "../src/core-profile";
import { CoreAccount } from "../src/core-account";
import { createCoreHandler } from "../src/core-server";

const root = mkdtempSync(join(tmpdir(), "core-account-"));
afterAll(() => rmSync(root, { force: true, recursive: true }));
function setup(name: string) {
  const config = initializeCore(join(root, name), 17851);
  let present = false;
  const dependencies = { close: async () => {}, present: () => present,
    login: async (_config: typeof config, options: Parameters<typeof import('../src/browser-login').loginToChatGpt>[1]) => {
      options?.onPhase?.("waiting_for_browser");
      await new Promise<void>((resolve, reject) => {
        const timer = setTimeout(resolve, 10);
        options?.signal?.addEventListener("abort", () => { clearTimeout(timer); reject(new Error("aborted")); }, { once: true });
      });
      present = true;
      return { storageStatePath: config.storageStatePath, accountSurfaceUrl: "https://chatgpt.com/", solAvailable: true, extraHighAvailable: false, proAvailable: false };
    } };
  return { config, dependencies, setPresent: (value: boolean) => { present = value; } };
}
async function idle(account: CoreAccount) {
  for (let i = 0; i < 100 && account.busy; i++) await Bun.sleep(5);
  expect(account.busy).toBe(false);
}
test("saved login, fresh login and completed inference are different facts", async () => {
  const { config, dependencies, setPresent } = setup("states");
  const account = new CoreAccount(config, async () => true, dependencies);
  expect(account.status().status).toBe("disconnected");
  setPresent(true);
  expect(account.status().status).toBe("saved");
  expect(account.status().test).toBe(null);
  account.start("login");
  expect(() => account.start("login")).toThrow("account_busy");
  await idle(account);
  expect(account.status().status).toBe("connected");
  expect(account.status().test).toBe(null);
  expect(account.status().models.some(item => item.id === "chatgpt-web/gpt-6-sol")).toBe(true);
  expect(() => account.select({ model: "chatgpt-web/gpt-6-sol", effort: "xhigh" })).toThrow();
  account.select({ model: "chatgpt-web/gpt-6-sol", effort: "high" });
  account.start("probe"); await idle(account);
  expect(account.status().test?.model).toBe("chatgpt-web/gpt-6-sol");
  const persisted = new CoreAccount(config, async () => true, dependencies);
  expect(persisted.status().selection?.model).toBe("chatgpt-web/gpt-6-sol");
  expect(persisted.status().status).toBe("saved");
  expect(JSON.stringify(account.status())).not.toContain(config.controlToken);
});
test("cancel waits for owned login cleanup and disconnect removes only its own browser state", async () => {
  const { config, dependencies } = setup("cancel");
  const account = new CoreAccount(config, async () => true, dependencies);
  account.start("login"); await account.cancel();
  expect(account.status().status).toBe("disconnected");
  expect(account.status().error).toBe(null);
  mkdirSync(dirname(config.storageStatePath), { recursive: true });
  writeFileSync(config.storageStatePath, "private-cookie-fixture");
  const unrelated = join(root, "another-profile"); writeFileSync(unrelated, "untouched");
  await account.disconnect();
  expect(existsSync(config.storageStatePath)).toBe(false);
  expect(existsSync(unrelated)).toBe(true);
});
test("account HTTP actions are authenticated, origin-blocked, bounded and cancel an active probe", async () => {
  const { config, dependencies, setPresent } = setup("http");
  setPresent(true); config.solAvailable = true;
  let handler: ReturnType<typeof createCoreHandler>;
  const account = new CoreAccount(config, async (_, signal) => {
    const result = await handler(new Request("http://127.0.0.1/v1/responses", { method: "POST", signal,
      headers: { authorization: `Bearer ${config.controlToken}` }, body: JSON.stringify({ model: "chatgpt-web/gpt-6-sol", input: "test" }) }));
    return result.ok;
  }, dependencies);
  handler = createCoreHandler(config, { account, loginPresent: () => true, respond: async req => {
    await new Promise<void>(resolve => req.signal.addEventListener("abort", () => resolve(), { once: true }));
    return Response.json({});
  } });
  const call = (action: string, body = {}, headers: Record<string, string> = {}) => handler(new Request(`http://127.0.0.1/core/account/${action}`, {
    method: "POST", headers: { authorization: `Bearer ${config.controlToken}`, ...headers }, body: JSON.stringify(body) }));
  expect((await call("login", {}, { origin: "http://foreign.example" })).status).toBe(403);
  expect((await call("login", {}, { authorization: "Bearer wrong" })).status).toBe(401);
  expect((await call("login", { home: "other" })).status).toBe(400);
  expect((await call("probe")).status).toBe(202);
  await Bun.sleep(10);
  expect((await call("cancel")).status).toBe(200);
  expect(account.busy).toBe(false);
  expect(account.status().test).toBe(null);
});
test("failed probe never publishes a successful connection test", async () => {
  const { config, dependencies, setPresent } = setup("failed");
  setPresent(true);
  const account = new CoreAccount(config, async () => false, dependencies);
  account.start("probe"); await idle(account);
  expect(account.status().status).toBe("error");
  expect(account.status().test).toBe(null);
  expect(account.status().error).toBe("probe_failed");
});

test("fresh accounts prefer GPT-6 Sol high while explicit saved choices win", () => {
  const { config, dependencies, setPresent } = setup("default-model");
  setPresent(true); config.solAvailable = true;
  const account = new CoreAccount(config, async () => true, dependencies);
  expect(account.status().selection).toEqual({ model: "chatgpt-web/gpt-6-sol", effort: "high" });
  account.select({ model: "chatgpt-web/gpt-6-sol", effort: "medium" });
  expect(new CoreAccount(config, async () => true, dependencies).status().selection)
    .toEqual({ model: "chatgpt-web/gpt-6-sol", effort: "medium" });
  config.solAvailable = false;
  const fallback = new CoreAccount(config, async () => true, dependencies).status();
  expect(fallback.models.some(model => model.id === fallback.selection?.model)).toBe(true);
});
