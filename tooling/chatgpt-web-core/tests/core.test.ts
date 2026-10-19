import { afterAll, expect, test } from "bun:test";
import { createHash } from "node:crypto";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { assertCoreProfile, initializeCore, loadCore } from "../src/core-profile";
import { createCoreHandler, validateCoreRequest } from "../src/core-server";
import { providerConfig } from "../src/config";
import { responseRequest } from "../src/server";
import { extractChatGptTurnIdentity, extractChatGptTurnUserRevision } from "../src/adapters/chatgpt-web/environment";
import { chatGptTurnExecutionKey, chatGptTurnRoundKey, chatGptThreadOwnershipKey } from "../src/adapters/chatgpt-web/turn-execution";

const root = mkdtempSync(join(tmpdir(), "chatgpt-core-test-"));
const oldEnvironment = Object.fromEntries(["CODEX_HOME", "CODEX_CHATGPT_WEB_HOME", "ANTIGRAVITY_COCKPIT_HOME", "VI_DUBBER_CORE_MODE", "TYPESAFE_ERROR_CLASSIFICATION", "TYPESAFE_TOOL_DISCOVERY"]
  .map(key => [key, process.env[key]]));
afterAll(() => {
  for (const [key, value] of Object.entries(oldEnvironment)) {
    if (value === undefined) delete process.env[key]; else process.env[key] = value;
  }
  rmSync(root, { recursive: true, force: true });
});
const home = join(root, "mt5");
const config = initializeCore(home, 17851);
const input = { model: "chatgpt-web/gpt-5.6-sol", input: "Draft a hypothetical strategy; no orders." };
function request(body: unknown = input, path = "/v1/responses", headers: Record<string, string> = {}) {
  return new Request(`http://127.0.0.1${path}`, { method: "POST",
    headers: { authorization: `Bearer ${config.controlToken}`, ...headers }, body: JSON.stringify(body) });
}

test("private initialization is idempotent and does not share homes or credentials", () => {
  const before = readFileSync(join(home, "config.json"), "utf8");
  expect(initializeCore(home, 17851).controlToken).toBe(config.controlToken);
  expect(readFileSync(join(home, "config.json"), "utf8")).toBe(before);
  expect(() => initializeCore(home, 17852)).toThrow("another port");
  const other = initializeCore(join(root, "vi"), 17850);
  expect(other.controlToken).not.toBe(config.controlToken);
  expect(other.storageStatePath).not.toBe(config.storageStatePath);
  expect(other.brokerSocketPath).not.toBe(config.brokerSocketPath);
  expect(providerConfig(config).chatgptWeb?.localToolsEnabled).toBe(false);
  expect(providerConfig(config).chatgptWeb?.providerOnly).toBe(true);
  expect(existsSync(join(home, "codex-compat", "config.toml"))).toBe(false);
  expect(() => initializeCore("relative-home", 17851)).toThrow("absolute");
  loadCore(home);
});

test("unsafe modes, tunnels and browser paths cannot use the core entrypoint", () => {
  for (const patch of [{ mode: "full" }, { integrationOwner: "standalone" }, { browserHost: "launcher" },
    { autoApproveToolCalls: true }, { experimentalSkillAttachments: true }, { experimentalBiggerContext: true },
    { storageStatePath: join(root, "other", "state.json") }, { tunnel: {} }]) {
    expect(() => assertCoreProfile({ ...config, ...patch } as typeof config, home)).toThrow("tool-free");
  }
});

test("tool registries, history references, agent payloads, attachments and metadata are refused", () => {
  for (const extra of [{ tools: [] }, { previous_response_id: "other-project" }, { metadata: {} },
    { client_metadata: {} }, { prompt_cache_key: "shared" }, { stream: true }, { store: true }]) {
    expect(() => validateCoreRequest({ ...input, ...extra })).toThrow();
  }
  for (const entry of [{ type: "function_call", name: "shell" }, { role: "tool", content: "result" },
    { role: "user", content: [{ type: "input_image", image_url: "file:///private" }] },
    { role: "user", content: "text", internal_chat_message_metadata_passthrough: {} }]) {
    expect(() => validateCoreRequest({ ...input, input: [entry] })).toThrow();
  }
  expect(validateCoreRequest({ ...input, input: [{ role: "user", content: [{ type: "input_text", text: "hello" }] }] }))
    .toMatchObject({ stream: false, store: false });
});

test("HTTP surface authenticates and does not expose agents, global controls or browser access", async () => {
  const handler = createCoreHandler(config);
  expect((await handler(request(input, "/v1/responses", { authorization: "wrong" }))).status).toBe(401);
  expect((await handler(request(input, "/v1/responses", { origin: "http://malicious.invalid" }))).status).toBe(403);
  expect((await handler(request({}, "/admin/drain"))).status).toBe(404);
  expect((await handler(request({}, "/v1/responses/compact"))).status).toBe(404);
  const health = await (await handler(new Request("http://127.0.0.1/healthz"))).json();
  expect(health).toMatchObject({ login_state_present: false, capabilities: { tools: false, agents: false, filesystem: false } });
  expect(JSON.stringify(health)).not.toContain(config.controlToken);
  const catalog = await handler(new Request("http://127.0.0.1/v1/models", { headers: { authorization: `Bearer ${config.controlToken}` } }));
  expect(catalog.status).toBe(200);
  expect(JSON.stringify(await catalog.json())).toContain("chatgpt-web/");
  expect((await handler(request())).status).toBe(503);
  expect((await handler(request({ ...input, tools: [] }))).status).toBe(400);
  expect((await handler(request({ ...input, input: "a".repeat(65536) }))).status).toBe(413);
});

test("validated requests cross the retained handler with clean headers and no response-state storage", async () => {
  let calls = 0;
  const identities: { thread_id: string; turn_id: string }[] = [];
  const handler = createCoreHandler(config, { loginPresent: () => true, respond: async (req, cfg, factory, options) => {
    calls++;
    expect(cfg.mode).toBe("browser-only");
    expect(options?.rememberState).toBe(false);
    expect(req.headers.has("authorization")).toBe(false);
    expect(req.headers.has("x-codex-turn-metadata")).toBe(false);
    const body = await req.json();
    const identity = body.client_metadata["x-codex-turn-metadata"];
    expect(identity.thread_id).toStartWith("core-");
    expect(identity.turn_id).toMatch(/^[0-9a-f-]{36}$/);
    expect(Object.keys(identity).sort()).toEqual(["thread_id", "turn_id"]);
    expect(body.input).toEqual([{ type: "message", role: "user", content: input.input,
      internal_chat_message_metadata_passthrough: { turn_id: identity.turn_id } }]);
    identities.push(identity);
    return Response.json({ status: "completed", output: [{ type: "message", content: [{ type: "output_text", text: "draft" }] }] });
  } });
  const response = await handler(request(input, "/v1/responses", { "x-codex-turn-metadata": "untrusted" }));
  expect((await response.json()).status).toBe("completed");
  expect(calls).toBe(1);
  await handler(request());
  expect(identities[1]!.thread_id).toBe(identities[0]!.thread_id);
  expect(identities[1]!.turn_id).not.toBe(identities[0]!.turn_id);
  expect(() => validateCoreRequest({ ...input, input: [{ role: "assistant", content: "no user turn" }] })).toThrow("user_message_required");
});

test("real loopback HTTP uses the retained Responses parser and envelope with a synthetic model adapter", async () => {
  let turns = 0;
  const handler = createCoreHandler(config, { loginPresent: () => true,
    respond: (req, cfg, _factory, options) => responseRequest(req, cfg, provider => ({
      name: "offline-contract-fixture",
      runTurn: async (parsed, incoming, emit) => {
        turns++;
        expect(provider.chatgptWeb?.localToolsEnabled).toBe(false);
        expect(parsed.context.tools ?? []).toHaveLength(0);
        expect(incoming.headers.has("authorization")).toBe(false);
        const identity = extractChatGptTurnIdentity(parsed);
        expect(identity.threadId).toStartWith("core-");
        expect(identity.turnId).toBeTruthy();
        expect(extractChatGptTurnUserRevision(parsed)).toBe(input.input);
        expect(chatGptTurnExecutionKey(parsed)).toBeTruthy();
        expect(chatGptTurnRoundKey(parsed)).toBeTruthy();
        expect(chatGptThreadOwnershipKey(parsed)).toBeTruthy();
        emit({ type: "text_delta", text: '{"draft":"synthetic"}' });
        emit({ type: "done", stopReason: "stop", endTurn: true });
      },
    }), options),
  });
  const server = Bun.serve({ hostname: "127.0.0.1", port: 0, fetch: handler });
  try {
    const response = await fetch(`http://127.0.0.1:${server.port}/v1/responses`, {
      method: "POST", headers: { authorization: `Bearer ${config.controlToken}` }, body: JSON.stringify(input),
    });
    const envelope = await response.json();
    expect(response.status).toBe(200);
    expect(envelope.status).toBe("completed");
    expect(JSON.stringify(envelope.output)).toContain("synthetic");
    expect(turns).toBe(1);
    expect(existsSync(join(home, "responses-state.json"))).toBe(false);
  } finally { await server.stop(true); }
});

test("single-flight admission, cancellation and failure release the request slot", async () => {
  let release!: () => void;
  const handler = createCoreHandler(config, { loginPresent: () => true, respond: async () => {
    await new Promise<void>(resolve => { release = resolve; });
    throw new Error("private provider details");
  } });
  const first = handler(request());
  while (!release) await Bun.sleep(1);
  expect((await handler(request())).status).toBe(429);
  release();
  const failed = await first;
  expect(failed.status).toBe(502);
  expect(await failed.text()).not.toContain("private provider details");
  const health = await (await handler(new Request("http://127.0.0.1/healthz"))).json();
  expect(health.active_requests).toBe(0);
  const timed = createCoreHandler(config, { timeoutMs: 10, loginPresent: () => true, respond: async req => {
    await new Promise<void>(resolve => req.signal.addEventListener("abort", () => resolve(), { once: true }));
    throw new Error("aborted");
  } });
  expect((await timed(request())).status).toBe(504);
});

test("source snapshot retains recorded transport bytes and license", () => {
  const base = resolve(import.meta.dir, "..");
  const manifest = JSON.parse(readFileSync(join(base, "SOURCE-MANIFEST.json"), "utf8"));
  expect(manifest.history_imported).toBe(false);
  for (const file of manifest.files) {
    if (file.path === "bun.lock") continue; // Only the root package name changed in the lock.
    expect(createHash("sha256").update(readFileSync(join(base, file.path))).digest("hex")).toBe(file.sha256);
  }
  expect(readFileSync(join(base, "LICENSE"), "utf8")).toContain("MIT License");
});

test("the public CLI refuses agent commands and cannot fall back to a global home", () => {
  for (const args of [["serve"], ["cockpit", "sync"], ["mcp"], ["setup"], ["subagents", "native"]]) {
    const process = Bun.spawnSync([Bun.which("bun")!, "run", resolve(import.meta.dir, "../src/core-cli.ts"), ...args]);
    expect(process.exitCode).not.toBe(0);
  }
});
