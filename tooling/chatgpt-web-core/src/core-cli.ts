import { browserLoginStateExists, loginToChatGpt } from "./browser-login";
import { saveConfig } from "./config";
import { closeChatGptBrowserWorkers } from "./adapters/chatgpt-web/browser-worker";
import { initializeCore, loadCore } from "./core-profile";
import { createCoreHandler } from "./core-server";

async function main() {
  const args = process.argv.slice(2);
  const command = args.shift();
  if (!command || command === "help" || command === "--help") {
    console.log("chatgpt-web-core <init|status|login|serve> --home <absolute private path> [--port <init port>]");
    return;
  }
  if (!["init", "status", "login", "serve"].includes(command)) throw new Error("Unsupported core command");
  const options = new Map<string, string>();
  while (args.length) {
    const option = args.shift()!;
    const value = args.shift();
    if (!["--home", "--port"].includes(option) || !value || options.has(option)) throw new Error("Invalid core options");
    options.set(option, value);
  }
  const home = options.get("--home");
  if (!home) throw new Error("--home is required; global profiles are never used");
  if (command !== "init" && options.has("--port")) throw new Error("--port is only supported by init");
  const config = command === "init" ? initializeCore(home, Number(options.get("--port"))) : loadCore(home);
  if (command === "init" || command === "status") {
    console.log(JSON.stringify({ service: "chatgpt-web-core", home, port: config.port, profile: "tool-free",
      login_state_present: browserLoginStateExists(config), transport_probed: false }));
    return;
  }
  if (command === "login") {
    const result = await loginToChatGpt(config);
    config.solAvailable = result.solAvailable;
    config.extraHighAvailable = result.extraHighAvailable;
    config.proAvailable = result.proAvailable;
    saveConfig(config);
    console.log("Dedicated login verified; account model capabilities updated.");
    return;
  }
  const server = Bun.serve({ hostname: "127.0.0.1", port: config.port, idleTimeout: 0,
    maxRequestBodySize: 65536, fetch: createCoreHandler(config) });
  let stopping = false;
  const stop = async () => {
    if (stopping) return;
    stopping = true;
    await server.stop(true);
    await closeChatGptBrowserWorkers();
    process.exit(0);
  };
  process.on("SIGINT", stop);
  process.on("SIGTERM", stop);
  console.log(`chatgpt-web-core listening on http://127.0.0.1:${server.port}; tool-free, one request at a time`);
}

if (import.meta.main) main().catch(error => {
  console.error(`chatgpt-web-core: ${error instanceof Error ? error.message : String(error)}`);
  process.exitCode = 1;
});
