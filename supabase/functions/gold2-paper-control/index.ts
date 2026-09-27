// GOLD2 broker-paper candidate. The handler is inert unless an operator sets
// all server-only secrets and GOLD2_PAPER_ENABLED=true after review.
import {handleRequest} from "./service.mjs";
import {validRuntimeBinding} from "./core.mjs";

function configuration() {
  const enabled = Deno.env.get("GOLD2_PAPER_ENABLED") === "true";
  const signalKey = Deno.env.get("GOLD2_SIGNAL_HMAC_KEY") ?? "";
  const runtimeKey = Deno.env.get("GOLD2_RUNTIME_HMAC_KEY") ?? "";
  const readerKey = Deno.env.get("GOLD2_BROKER_READER_HMAC_KEY") ?? "";
  const binding = {
    environment: "SIMNOW_FIRST_NORMAL",
    accountId: Deno.env.get("GOLD2_RUNTIME_ACCOUNT_ID") ?? "",
    robotId: Number(Deno.env.get("GOLD2_RUNTIME_ROBOT_ID") ?? "0"),
    sourceSha256: Deno.env.get("GOLD2_RUNTIME_SOURCE_SHA256") ?? "",
    readerSourceSha256: Deno.env.get("GOLD2_BROKER_READER_SOURCE_SHA256") ?? "",
  };
  let builtInSecret = "";
  try {
    const secrets = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") ?? "{}");
    if (typeof secrets.default === "string") builtInSecret = secrets.default;
  } catch { return null; }
  const dbKey = Deno.env.get("GOLD2_DB_SECRET_KEY") || builtInSecret
    || Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
  const legacyServiceKey = dbKey === Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") && dbKey.startsWith("eyJ");
  const projectRef = Deno.env.get("GOLD2_SUPABASE_PROJECT_REF") ?? "";
  const url = Deno.env.get("SUPABASE_URL") ?? "";
  const expectedUrl = `https://${projectRef}.supabase.co`;
  if (!enabled || signalKey.length < 32 || runtimeKey.length < 32
      || readerKey.length < 32 || new Set([signalKey, runtimeKey, readerKey]).size !== 3
      || !validRuntimeBinding(binding) || !(dbKey.startsWith("sb_secret_") || legacyServiceKey)
      || !/^[a-z0-9]{20}$/.test(projectRef) || url !== expectedUrl) {
    return null;
  }
  return {signalKey, runtimeKey, readerKey, binding, dbKey, url,
    controlSigning: {
      privateKeyBase64: Deno.env.get("GOLD2_CONTROL_ED25519_PKCS8_BASE64") ?? "",
      publicKeyBase64: Deno.env.get("GOLD2_CONTROL_ED25519_PUBLIC_BASE64") ?? "",
    },
    claimEnabled: Deno.env.get("GOLD2_CLAIM_ENABLED") === "true"};
}

async function rpc(config: NonNullable<ReturnType<typeof configuration>>, name: string, args: Record<string, unknown>) {
  const response = await fetch(`${config.url}/rest/v1/rpc/${name}`, {
    method: "POST",
    headers: {"apikey": config.dbKey, "content-type": "application/json",
      ...(config.dbKey.startsWith("eyJ") ? {authorization: `Bearer ${config.dbKey}`} : {})},
    body: JSON.stringify(args),
    signal: AbortSignal.timeout(5000),
  });
  if (!response.ok) throw new Error("REMOTE_RPC_DENIED_OR_UNKNOWN");
  const raw = await response.text();
  if (raw.length > 2_100_000) throw new Error("REMOTE_RPC_OVERSIZED");
  return JSON.parse(raw);
}

Deno.serve((request) => {
  const config = configuration();
  return handleRequest(request, {
    enabled: config !== null,
    // Default false; explicit acceptance and all binding/key checks required.
    // V1 command-only claim remains permanently denied by service.mjs.
    claimEnabled: config?.claimEnabled === true,
    signalKey: config?.signalKey,
    runtimeKey: config?.runtimeKey,
    readerKey: config?.readerKey,
    binding: config?.binding,
    controlSigning: config?.controlSigning,
    rpc: config ? (name: string, args: Record<string, unknown>) => rpc(config, name, args) : null,
  });
});
