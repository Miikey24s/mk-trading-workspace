import { randomUUID, timingSafeEqual } from "node:crypto";
import { browserLoginStateExists } from "./browser-login";
import type { AppConfig } from "./config";
import type { CoreAccount } from "./core-account";
import { modelsRequest, responseRequest } from "./server";

const MAX_BYTES = 65536;
const ALLOWED_FIELDS = new Set(["model", "instructions", "input", "reasoning", "stream", "store", "text", "max_output_tokens"]);
type CoreDependencies = {
  account?: CoreAccount;
  models?: typeof modelsRequest;
  respond?: typeof responseRequest;
  loginPresent?: typeof browserLoginStateExists;
  timeoutMs?: number;
};

function failure(status: number, code: string): Response {
  return Response.json({ error: { type: "core_error", code, message: code } }, { status });
}

export function validateCoreRequest(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("invalid_request");
  const body = value as Record<string, unknown>;
  if (Object.keys(body).some(key => !ALLOWED_FIELDS.has(key))) throw new Error("unsupported_request_field");
  if (typeof body.model !== "string" || !body.model.startsWith("chatgpt-web/")) throw new Error("chatgpt_web_model_required");
  if (body.stream !== undefined && body.stream !== false) throw new Error("streaming_not_supported");
  if (body.store !== undefined && body.store !== false) throw new Error("response_storage_not_supported");
  if (body.instructions !== undefined && typeof body.instructions !== "string") throw new Error("invalid_instructions");
  if (typeof body.input === "string") {
    if (!body.input.trim()) throw new Error("empty_input");
  } else if (Array.isArray(body.input) && body.input.length > 0 && body.input.length <= 64) {
    for (const message of body.input) {
      if (!message || typeof message !== "object" || Array.isArray(message)
        || Object.keys(message).some(key => !["type", "role", "content"].includes(key))
        || (message.type !== undefined && message.type !== "message")
        || !["user", "assistant"].includes(message.role)) throw new Error("text_messages_required");
      if (typeof message.content === "string") continue;
      if (!Array.isArray(message.content) || message.content.length === 0 || message.content.length > 64
        || message.content.some((part: unknown) => !part || typeof part !== "object" || Array.isArray(part)
          || Object.keys(part).some(key => !["type", "text"].includes(key))
          || (part as { type?: unknown }).type !== "input_text"
          || typeof (part as { text?: unknown }).text !== "string")) throw new Error("text_messages_required");
    }
  } else throw new Error("text_input_required");
  if (Array.isArray(body.input) && body.input.at(-1).role !== "user") throw new Error("user_message_required");
  return { ...body, stream: false, store: false };
}

async function readBoundedJson(req: Request): Promise<unknown> {
  if (Number(req.headers.get("content-length")) > MAX_BYTES) throw new Error("payload_too_large");
  if (req.headers.has("content-encoding")) throw new Error("encoded_requests_not_supported");
  const reader = req.body?.getReader();
  if (!reader) throw new Error("invalid_request");
  const signal = AbortSignal.any([req.signal, AbortSignal.timeout(10000)]);
  const cancel = () => { void reader.cancel(); };
  signal.addEventListener("abort", cancel, { once: true });
  const chunks: Uint8Array[] = [];
  let length = 0;
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (signal.aborted) throw new Error("request_cancelled");
      if (done) break;
      length += value.byteLength;
      if (length > MAX_BYTES) throw new Error("payload_too_large");
      chunks.push(value);
    }
  } finally {
    signal.removeEventListener("abort", cancel);
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function createCoreHandler(config: AppConfig, dependencies: CoreDependencies = {}) {
  const threadId = `core-${randomUUID()}`;
  let busy = false;
  let managingAccount = false;
  return async (req: Request): Promise<Response> => {
    const path = new URL(req.url).pathname;
    // Browser pages cannot use the caller's private local transport.
    if (req.headers.has("origin")) return failure(403, "browser_origin_not_allowed");
    if (req.method === "GET" && path === "/healthz") {
      return Response.json({ service: "chatgpt-web-core", profile: "tool-free", active_requests: busy ? 1 : 0,
        login_state_present: (dependencies.loginPresent ?? browserLoginStateExists)(config),
        capabilities: { text: true, tools: false, agents: false, filesystem: false },
        limits: { max_payload_bytes: MAX_BYTES, max_concurrency: 1, timeout_ms: dependencies.timeoutMs ?? 180000 } });
    }
    const expected = Buffer.from(`Bearer ${config.controlToken}`);
    const actual = Buffer.from(req.headers.get("authorization") ?? "");
    if (actual.length !== expected.length || !timingSafeEqual(actual, expected)) return failure(401, "unauthorized");
    if (dependencies.account && path.startsWith("/core/account")) {
      const account = dependencies.account;
      if (req.method === "GET" && path === "/core/account") return Response.json(account.status());
      if (req.method !== "POST" || !["login", "probe", "selection", "cancel", "disconnect"].some(action => path === `/core/account/${action}`)) return failure(404, "not_found");
      if (managingAccount) return failure(409, "account_busy");
      if (busy && !(account.busy && (path.endsWith("/cancel") || path.endsWith("/disconnect")))) return failure(409, "provider_busy");
      managingAccount = true;
      try {
        const body = await readBoundedJson(req);
        if (path.endsWith("/selection")) return Response.json(account.select(body));
        if (!body || typeof body !== "object" || Array.isArray(body) || Object.keys(body).length) return failure(400, "invalid_request");
        if (path.endsWith("/cancel")) return Response.json(await account.cancel());
        if (path.endsWith("/disconnect")) return Response.json(await account.disconnect());
        return Response.json(account.start(path.endsWith("/login") ? "login" : "probe"), { status: 202 });
      } catch (error) {
        const code = error instanceof Error && ["account_busy", "login_required", "invalid_selection"].includes(error.message) ? error.message : "account_action_failed";
        return failure(code === "account_busy" ? 409 : 400, code);
      } finally { managingAccount = false; }
    }
    if (req.method === "GET" && path === "/v1/models") return (dependencies.models ?? modelsRequest)(req, config);
    if (req.method !== "POST" || path !== "/v1/responses") return failure(404, "not_found");
    if (busy || managingAccount || dependencies.account?.status().operation?.kind === "login") return failure(429, "provider_busy");
    busy = true;
    const deadline = AbortSignal.timeout(dependencies.timeoutMs ?? 180000);
    try {
      let body: Record<string, unknown>;
      try { body = validateCoreRequest(await readBoundedJson(req)); }
      catch (error) {
        const code = error instanceof SyntaxError ? "invalid_json" : error instanceof Error ? error.message : "invalid_request";
        return failure(code === "payload_too_large" ? 413 : 400, code);
      }
      if (!(dependencies.loginPresent ?? browserLoginStateExists)(config)) return failure(503, "login_required");
      const signal = AbortSignal.any([req.signal, deadline]);
      // Upstream owns browser turns by identity even without tools. Generate it here,
      // after validation; accepting caller lifecycle metadata would mix app ownership.
      const turnId = randomUUID();
      const input: Record<string, unknown>[] = typeof body.input === "string"
        ? [{ type: "message", role: "user", content: body.input }]
        : (body.input as Record<string, unknown>[]).map(message => ({ ...message, type: "message" }));
      const last = input.length - 1;
      input[last] = { ...input[last], internal_chat_message_metadata_passthrough: { turn_id: turnId } };
      // Rebuild headers and body so no Codex identity, tool registry or prior-response state enters the bridge.
      const clean = new Request("http://127.0.0.1/v1/responses", {
        method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ ...body, input, client_metadata: { "x-codex-turn-metadata": { thread_id: threadId, turn_id: turnId } } }), signal,
      });
      const result = await (dependencies.respond ?? responseRequest)(clean, config, undefined, { rememberState: false });
      if (deadline.aborted) return failure(504, "provider_timeout");
      if (req.signal.aborted) return failure(499, "client_cancelled");
      return result;
    } catch {
      if (req.signal.aborted) return failure(499, "client_cancelled");
      return deadline.aborted ? failure(504, "provider_timeout") : failure(502, "provider_failed");
    } finally { busy = false; }
  };
}
