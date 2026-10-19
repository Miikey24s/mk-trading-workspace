import { existsSync, readFileSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { browserLoginStateExists, loginToChatGpt } from "./browser-login";
import { atomicWriteFile, saveConfig, type AppConfig } from "./config";
import { closeChatGptBrowserWorkers } from "./adapters/chatgpt-web/browser-worker";
import { availableChatGptWebModelRoutes, chatGptWebRouteEfforts, requireChatGptWebModelRoute } from "./chatgpt-web-models";

type Selection = { model: string; effort: string };
type Operation = { kind: "login" | "probe"; phase: string; started_at: string };
type Dependencies = {
  login?: typeof loginToChatGpt;
  close?: typeof closeChatGptBrowserWorkers;
  present?: typeof browserLoginStateExists;
};

/** One machine-local account, owned by this private profile. No cookie or token leaves it. */
export class CoreAccount {
  private operation?: Operation;
  private controller?: AbortController;
  private pending?: Promise<void>;
  private failure?: string;
  private verifiedAt?: string;
  private tested?: Selection & { at: string };
  private selection?: Selection;
  private readonly settingsPath: string;

  constructor(private config: AppConfig,
    private probe: (selection: Selection, signal: AbortSignal) => Promise<boolean>,
    private dependencies: Dependencies = {}) {
    this.settingsPath = join(dirname(config.storageStatePath), "../account-settings.json");
    try {
      const value = JSON.parse(readFileSync(this.settingsPath, "utf8"));
      this.validateSelection(value);
      this.selection = { model: value.model, effort: value.effort };
    } catch { /* A stale selection must not enable an unavailable account mode. */ }
  }

  get busy() { return !!this.operation; }
  private present() { return (this.dependencies.present ?? browserLoginStateExists)(this.config); }
  private catalog() {
    return availableChatGptWebModelRoutes(this.config).filter(route => route.interactionMode === "automatic")
      .map(route => ({ id: route.slug, name: route.displayName, efforts: chatGptWebRouteEfforts(route, this.config) }));
  }
  private validateSelection(value: unknown): asserts value is Selection {
    if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("invalid_selection");
    const input = value as Record<string, unknown>;
    if (Object.keys(input).some(key => !["model", "effort"].includes(key))
      || typeof input.model !== "string" || typeof input.effort !== "string") throw new Error("invalid_selection");
    const route = requireChatGptWebModelRoute(input.model, this.config, input.effort);
    if (route.interactionMode !== "automatic") throw new Error("invalid_selection");
  }
  status() {
    const present = this.present();
    const models = present ? this.catalog() : [];
    const preferred = models.find(model => model.id === "chatgpt-web/gpt-6-sol") ?? models[0];
    const selection = models.some(model => model.id === this.selection?.model && model.efforts.includes(this.selection.effort as never))
      ? this.selection : preferred ? { model: preferred.id, effort: preferred.efforts.includes("high") ? "high" : preferred.efforts[0] } : null;
    return { service: "chatgpt-web-core", account_scope: "local-machine", status: this.operation ? this.operation.phase
      : this.failure ? "error" : present ? this.verifiedAt ? "connected" : "saved" : "disconnected",
      login_state_present: present, verified_at: this.verifiedAt ?? null, operation: this.operation ?? null,
      error: this.failure ?? null, selection, models, model_catalog_verified: false,
      test: this.tested ?? null, capabilities: { text: true, tools: false, agents: false } };
  }
  select(value: unknown) {
    if (this.busy) throw new Error("account_busy");
    if (!this.present()) throw new Error("login_required");
    this.validateSelection(value);
    this.selection = { model: value.model, effort: value.effort };
    this.tested = undefined;
    atomicWriteFile(this.settingsPath, JSON.stringify(this.selection) + "\n");
    return this.status();
  }
  start(kind: "login" | "probe") {
    if (this.busy) throw new Error("account_busy");
    if (kind === "probe" && !this.present()) throw new Error("login_required");
    const selected = this.status().selection as Selection | null;
    this.failure = undefined;
    this.tested = undefined;
    const controller = this.controller = new AbortController();
    this.operation = { kind, phase: kind === "login" ? "opening_browser" : "testing", started_at: new Date().toISOString() };
    this.pending = (async () => {
      try {
        await (this.dependencies.close ?? closeChatGptBrowserWorkers)();
        controller.signal.throwIfAborted();
        if (kind === "login") {
          const result = await (this.dependencies.login ?? loginToChatGpt)(this.config, {
            signal: controller.signal, onPhase: phase => { if (this.operation) this.operation.phase = phase; },
          });
          controller.signal.throwIfAborted();
          this.config.solAvailable = result.solAvailable;
          this.config.extraHighAvailable = result.extraHighAvailable;
          this.config.proAvailable = result.proAvailable;
          saveConfig(this.config);
          this.selection = undefined;
          this.verifiedAt = new Date().toISOString();
        } else {
          if (!selected || !await this.probe(selected, controller.signal)) throw new Error("probe_failed");
          controller.signal.throwIfAborted();
          this.tested = { ...selected, at: new Date().toISOString() };
          this.verifiedAt = this.tested.at;
        }
      } catch {
        if (!controller.signal.aborted) this.failure = kind === "login" ? "login_failed" : "probe_failed";
      } finally {
        this.operation = undefined;
        this.controller = undefined;
      }
    })();
    return this.status();
  }
  async cancel() {
    this.controller?.abort();
    await this.pending;
    this.failure = undefined;
    return this.status();
  }
  async disconnect() {
    await this.cancel();
    await (this.dependencies.close ?? closeChatGptBrowserWorkers)();
    const browserRoot = dirname(this.config.storageStatePath);
    // Core profile validation restricts this directory to the dedicated private home.
    if (existsSync(browserRoot)) rmSync(browserRoot, { recursive: true, force: true });
    this.config.solAvailable = false;
    this.config.extraHighAvailable = false;
    this.config.proAvailable = false;
    saveConfig(this.config);
    this.selection = undefined;
    this.verifiedAt = undefined;
    this.tested = undefined;
    rmSync(this.settingsPath, { force: true });
    return this.status();
  }
}
