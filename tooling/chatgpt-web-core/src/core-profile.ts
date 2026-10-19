import { existsSync, realpathSync } from "node:fs";
import { isAbsolute, join, relative, resolve, sep } from "node:path";
import { defaultConfig, getConfigPath, loadConfig, saveConfig, type AppConfig } from "./config";

export function bindCoreHome(home: string): string {
  if (!isAbsolute(home)) throw new Error("--home must be an absolute, private runtime directory");
  const privateHome = resolve(home);
  process.env.CODEX_CHATGPT_WEB_HOME = privateHome;
  process.env.CODEX_HOME = join(privateHome, "codex-compat");
  process.env.ANTIGRAVITY_COCKPIT_HOME = join(privateHome, "cockpit-compat");
  // Retain the existing write-boundary guard from the extracted VI core.
  process.env.VI_DUBBER_CORE_MODE = "isolated-provider";
  process.env.TYPESAFE_ERROR_CLASSIFICATION = "off";
  process.env.TYPESAFE_TOOL_DISCOVERY = "off";
  return privateHome;
}

export function assertCoreProfile(config: AppConfig, home: string): void {
  const browserRoot = join(home, "browser");
  const stateRelative = relative(browserRoot, config.storageStatePath);
  if (config.mode !== "browser-only" || config.integrationOwner !== "cockpit"
    || config.host !== "127.0.0.1" || config.browserHost !== "managed-chrome"
    || config.browserInteractionMode !== "automatic" || config.autoApproveToolCalls
    || config.experimentalSkillAttachments || config.experimentalBiggerContext
    || config.tunnel || config.automaticTunnel || config.manualTunnel || config.purpose
    || !stateRelative || stateRelative === ".." || stateRelative.startsWith(`..${sep}`)
    || isAbsolute(stateRelative)) {
    throw new Error("Configuration is not an isolated, tool-free chatgpt-web-core profile");
  }
  // A private-looking path must not redirect browser credentials into another profile.
  for (const path of [home, browserRoot, config.storageStatePath]) {
    if (existsSync(path) && resolve(realpathSync(path)).toLowerCase() !== resolve(path).toLowerCase()) {
      throw new Error("Runtime home and browser state must not be links to another profile");
    }
  }
}

export function initializeCore(home: string, port: number): AppConfig {
  if (!Number.isInteger(port) || port < 1024 || port > 65535) throw new Error("--port must be 1024..65535");
  bindCoreHome(home);
  if (existsSync(getConfigPath())) {
    const config = loadCore(home);
    if (config.port !== port) throw new Error("Existing runtime uses another port; select a separate home");
    return config;
  }
  const config = defaultConfig("browser-only");
  config.integrationOwner = "cockpit";
  config.port = port;
  assertCoreProfile(config, home);
  saveConfig(config);
  return config;
}

export function loadCore(home: string): AppConfig {
  bindCoreHome(home);
  const config = loadConfig();
  assertCoreProfile(config, home);
  return config;
}
