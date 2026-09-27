// Pure protocol checks shared by the Edge entry and offline Node tests.
// No credentials, network calls, broker calls or Supabase client live here.
const encoder = new TextEncoder();
export const MAX_BODY_BYTES = 2_100_000;
const SHA = /^sha256:[0-9a-f]{64}$/;
const HEX = /^[0-9a-f]{64}$/;
const ID = /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$/;
const EVENT_KEYS = ["at", "command_id", "data", "event_hash", "kind", "previous_hash", "sequence"];
const SIGNAL_KEYS = [
  "decision_at", "forward_decision_id", "forward_decision_sha256",
  "frozen_dataset_sha256", "outcome_contracts", "parameters_sha256",
  "record_id", "recorded_at", "registry_id", "signal_id", "signal_sha256",
  "source_ref",
];
const SCOPES = Object.freeze({
  signal: new Set(["anchor_signal", "read_signal"]),
  broker_reader: new Set(["ingest_broker_evidence_v2", "read_broker_evidence_v2", "ingest_native_evidence_v3", "read_native_evidence_v3"]),
  runtime: new Set(["append_ledger", "read_ledger", "claim_order", "read_claim", "claim_order_v2", "read_account_state_v2", "read_claim_v2", "record_submit_attempt_v2", "record_terminal_v2", "freeze_account_v2", "claim_linked_exit_v3", "complete_linked_pair_v3"]),
});

export class Denied extends Error {
  constructor(code) { super(code); this.code = code; }
}

function codePointCompare(left, right) {
  const a = Array.from(left, c => c.codePointAt(0));
  const b = Array.from(right, c => c.codePointAt(0));
  for (let i = 0; i < Math.min(a.length, b.length); i++) {
    if (a[i] !== b[i]) return a[i] - b[i];
  }
  return a.length - b.length;
}

export function canonical(value, depth = 0) {
  if (depth > 64) throw new Denied("JSON_TOO_DEEP");
  if (value === null || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "string") {
    try { encodeURIComponent(value); } catch { throw new Denied("INVALID_UNICODE"); }
    return JSON.stringify(value);
  }
  // Python's canonical JSON preserves 1.0, whereas JS parsing erases the
  // float/integer distinction. This service accepts only safe integers.
  if (typeof value === "number") {
    if (!Number.isSafeInteger(value)) throw new Denied("NON_INTEGER_JSON_NUMBER");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return "[" + value.map(v => canonical(v, depth + 1)).join(",") + "]";
  if (typeof value === "object" && value !== undefined) {
    const keys = Object.keys(value).sort(codePointCompare);
    return "{" + keys.map(k => canonical(k, depth + 1) + ":" + canonical(value[k], depth + 1)).join(",") + "}";
  }
  throw new Denied("UNSUPPORTED_JSON_VALUE");
}

function hex(bytes) { return Array.from(new Uint8Array(bytes), b => b.toString(16).padStart(2, "0")).join(""); }
export async function sha256(value) {
  const bytes = typeof value === "string" ? encoder.encode(value) : value;
  return hex(await crypto.subtle.digest("SHA-256", bytes));
}
export async function objectHash(value) { return "sha256:" + await sha256(canonical(value)); }

function exactKeys(value, keys) {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    && Object.keys(value).sort(codePointCompare).join("\0") === [...keys].sort(codePointCompare).join("\0");
}
function identifier(value) { return typeof value === "string" && ID.test(value); }
function robotId(value) { return Number.isSafeInteger(value) && value > 0; }
function instant(value) { return typeof value === "string" && Number.isFinite(Date.parse(value)) && /(?:Z|[+-]\d\d:\d\d)$/.test(value); }

export async function validateSignal(input) {
  if (!exactKeys(input, ["op", "record", "record_sha256", "registry_root_sha256"])) throw new Denied("SIGNAL_REQUEST_SHAPE");
  const record = input.record;
  if (!exactKeys(record, SIGNAL_KEYS) || !identifier(record.registry_id) || !identifier(record.record_id)
      || !instant(record.decision_at) || !instant(record.recorded_at)
      || !SHA.test(input.record_sha256) || !SHA.test(input.registry_root_sha256)) throw new Denied("SIGNAL_RECORD_SHAPE");
  if (await objectHash(record) !== input.record_sha256) throw new Denied("SIGNAL_HASH_MISMATCH");
  return {
    p_registry_id: record.registry_id, p_record_id: record.record_id,
    p_record_sha256: input.record_sha256,
    p_registry_root_sha256: input.registry_root_sha256,
    p_decision_at: record.decision_at, p_recorded_at: record.recorded_at,
    p_record: record,
  };
}

export async function validateLedger(input) {
  if (!exactKeys(input, ["op", "account_id", "robot_id", "events", "root_hash"])
      || !identifier(input.account_id) || !robotId(input.robot_id)
      || !Array.isArray(input.events) || input.events.length < 1 || input.events.length > 10000
      || !SHA.test(input.root_hash)) throw new Denied("LEDGER_REQUEST_SHAPE");
  let previous = "0".repeat(64);
  for (let index = 0; index < input.events.length; index++) {
    const event = input.events[index];
    if (!exactKeys(event, EVENT_KEYS) || event.sequence !== index + 1
        || !identifier(event.command_id) || !instant(event.at)
        || typeof event.kind !== "string" || !/^[A-Z][A-Za-z]+$/.test(event.kind)
        || event.previous_hash !== previous || !SHA.test(event.event_hash)
        || event.data === null || typeof event.data !== "object" || Array.isArray(event.data)) {
      throw new Denied("LEDGER_CHAIN_SHAPE");
    }
    const { event_hash: claimed, ...material } = event;
    if (await objectHash(material) !== claimed) throw new Denied("LEDGER_EVENT_HASH_MISMATCH");
    previous = claimed;
  }
  if (previous !== input.root_hash) throw new Denied("LEDGER_ROOT_MISMATCH");
  return {p_account_id: input.account_id, p_robot_id: input.robot_id,
          p_events: input.events, p_root_hash: input.root_hash};
}

export function validateClaim(input) {
  if (!exactKeys(input, ["op", "command_id", "account_id", "robot_id", "contract_hash"])
      || !identifier(input.command_id) || !identifier(input.account_id)
      || !robotId(input.robot_id) || !SHA.test(input.contract_hash)) throw new Denied("CLAIM_REQUEST_SHAPE");
  return {p_command_id: input.command_id, p_account_id: input.account_id,
          p_robot_id: input.robot_id, p_contract_hash: input.contract_hash};
}

export function validateRead(input) {
  if (input.op === "read_signal" && exactKeys(input, ["op", "registry_id", "record_id"])
      && identifier(input.registry_id) && identifier(input.record_id)) {
    return {p_registry_id: input.registry_id, p_record_id: input.record_id};
  }
  if (input.op === "read_ledger" && exactKeys(input, ["op", "account_id", "robot_id"])
      && identifier(input.account_id) && robotId(input.robot_id)) {
    return {p_account_id: input.account_id, p_robot_id: input.robot_id};
  }
  if (input.op === "read_claim" && exactKeys(input, ["op", "command_id"])
      && identifier(input.command_id)) return {p_command_id: input.command_id};
  throw new Denied("READ_REQUEST_SHAPE");
}

export async function readBounded(request) {
  const declared = request.headers.get("content-length");
  if (declared !== null && (!/^\d+$/.test(declared) || Number(declared) > MAX_BODY_BYTES)) throw new Denied("BODY_TOO_LARGE");
  if (!request.body) throw new Denied("BODY_REQUIRED");
  const reader = request.body.getReader();
  const chunks = [];
  let length = 0;
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    length += value.length;
    if (length > MAX_BODY_BYTES) { await reader.cancel(); throw new Denied("BODY_TOO_LARGE"); }
    chunks.push(value);
  }
  const result = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) { result.set(chunk, offset); offset += chunk.length; }
  return result;
}

export async function authenticate(request, bytes, secrets, nowMs = Date.now()) {
  if (request.method !== "POST" || !request.headers.get("content-type")?.toLowerCase().startsWith("application/json")) throw new Denied("REQUEST_METHOD_OR_TYPE");
  const role = request.headers.get("x-gold2-role");
  const timestamp = request.headers.get("x-gold2-timestamp");
  const signature = request.headers.get("x-gold2-signature");
  const key = role === "signal" ? secrets.signal : role === "runtime" ? secrets.runtime : role === "broker_reader" ? secrets.reader : null;
  if (!key || encoder.encode(key).length < 32 || !instant(timestamp)
      || Math.abs(nowMs - Date.parse(timestamp)) > 30_000
      || !signature || !/^sha256=[0-9a-f]{64}$/.test(signature)) throw new Denied("AUTH_DENIED");
  const material = "GOLD2-PAPER-V1\n" + request.method + "\n" + new URL(request.url).pathname
    + "\n" + timestamp + "\n" + await sha256(bytes);
  const cryptoKey = await crypto.subtle.importKey("raw", encoder.encode(key), {name: "HMAC", hash: "SHA-256"}, false, ["verify"]);
  const claimed = new Uint8Array(signature.slice(7).match(/.{2}/g).map(x => parseInt(x, 16)));
  if (!await crypto.subtle.verify("HMAC", cryptoKey, claimed, encoder.encode(material))) throw new Denied("AUTH_DENIED");
  return role;
}

export async function prepareOperation(input, role, nowMs = Date.now()) {
  if (!input || typeof input !== "object" || Array.isArray(input)
      || !SCOPES[role]?.has(input.op)) throw new Denied("OPERATION_SCOPE_DENIED");
  if (["claim_linked_exit_v3", "complete_linked_pair_v3"].includes(input.op)) {
    return ["gold2_paper_" + input.op, validateLinkedOperation(input)];
  }
  if (input.op === "ingest_native_evidence_v3") return ["gold2_paper_ingest_native_evidence_v3", await validateNativeEvidence(input, nowMs)];
  if (input.op === "read_native_evidence_v3") {
    const args = commonV2(input, [...COMMON_V2, "evidence_id"]);
    if (!identifier(input.evidence_id)) throw new Denied("NATIVE_EVIDENCE_ID_DENIED");
    return ["gold2_paper_read_native_evidence_v3", {...args, p_evidence_id: input.evidence_id}];
  }
  if (V2_RUNTIME_OPS.has(input.op)) return ["gold2_paper_" + input.op, validateCoordinator(input)];
  if (input.op === "read_broker_evidence_v2") {
    const args = commonV2(input, [...COMMON_V2, "evidence_id"]);
    if (!identifier(input.evidence_id)) throw new Denied("V2_EVIDENCE_REFERENCE_REQUIRED");
    return ["gold2_paper_read_broker_evidence_v2", {...args, p_evidence_id: input.evidence_id}];
  }
  if (input.op === "ingest_broker_evidence_v2") return ["gold2_paper_ingest_broker_evidence_v2", await validateEvidence(input, nowMs)];
  switch (input.op) {
    case "anchor_signal": return ["gold2_paper_anchor_signal_v1", await validateSignal(input)];
    case "append_ledger": return ["gold2_paper_append_ledger_v1", await validateLedger(input)];
    case "claim_order": return ["gold2_paper_claim_order_v1", validateClaim(input)];
    case "read_signal": return ["gold2_paper_read_signal_v1", validateRead(input)];
    case "read_ledger": return ["gold2_paper_read_ledger_v1", validateRead(input)];
    case "read_claim": return ["gold2_paper_read_claim_v1", validateRead(input)];
    default: throw new Denied("OPERATION_SCOPE_DENIED");
  }
}

export async function signalProof(readback, verifiedAt) {
  if (!readback || !SHA.test(readback.record_sha256) || !SHA.test(readback.registry_root_sha256)
      || !instant(readback.anchor_received_at) || !instant(verifiedAt)
      || readback.record?.registry_id !== readback.registry_id
      || readback.record?.record_id !== readback.record_id
      || Date.parse(readback.record?.recorded_at) !== Date.parse(readback.recorded_at)
      || Date.parse(readback.record?.decision_at) !== Date.parse(readback.decision_at)
      || await objectHash(readback.record) !== readback.record_sha256) throw new Denied("REMOTE_SIGNAL_READBACK_INVALID");
  const proof = {
    status: "VERIFIED_EXTERNAL_TIME_AND_INCLUSION",
    verifier_identity: "GOLD2_PAPER_SUPABASE_EDGE_V1",
    registry_id: readback.registry_id,
    record_id: readback.record_id,
    record_sha256: readback.record_sha256,
    registry_root_sha256: readback.registry_root_sha256,
    recorded_at: readback.recorded_at,
    anchor_received_at: readback.anchor_received_at,
  };
  return {...proof, proof_sha256: await objectHash(proof), verified_at: verifiedAt};
}

// V2 broker facts are admitted only by a separate, bound reader principal.
// A HMAC is provenance for the configured reader, not evidence that CTP ran.
export const ENVIRONMENT = "SIMNOW_FIRST_NORMAL";
export const COORDINATOR_SOURCE = "external_account_coordinator_v2";
const COMMON_V2 = ["op", "environment", "account_id", "robot_id", "source_sha256"];
const MUTATION_V2 = [...COMMON_V2, "expected_version", "ledger_root_hash", "ledger_sequence"];
const FACT_KEYS = ["command_id", "claim_id", "instrument", "action", "order_id", "order_status",
  "filled_quantity", "position_quantity", "pending_order_count", "reconciliation",
  "raw_account_sha256", "raw_orders_sha256", "raw_trades_sha256", "raw_positions_sha256"];
const BALANCE_KEYS = ["cash_cents", "available_cents", "frozen_margin_cents", "position_quantity", "filled_quantity"];
export const V2_RUNTIME_OPS = new Set(["claim_order_v2", "read_account_state_v2", "read_claim_v2",
  "record_submit_attempt_v2", "record_terminal_v2", "freeze_account_v2", "claim_linked_exit_v3", "complete_linked_pair_v3"]);
function quantity(value) { return value === 0 || value === 1; }
function version(value) { return Number.isSafeInteger(value) && value >= 0; }
function au(value) { return typeof value === "string" && /^au\d{4}$/.test(value); }
function action(value) { return value === "OPEN_LONG" || value === "CLOSE_LONG"; }
function nullableId(value) { return value === null || identifier(value); }
export function validRuntimeBinding(binding) {
  return binding && binding.environment === ENVIRONMENT && identifier(binding.accountId)
    && robotId(binding.robotId) && SHA.test(binding.sourceSha256)
    && SHA.test(binding.readerSourceSha256) && binding.sourceSha256 !== binding.readerSourceSha256;
}
export function assertRoleBinding(input, role, binding) {
  if (role === "signal") return;
  if (!validRuntimeBinding(binding)) throw new Denied("ROLE_BINDING_REQUIRED");
  if (input.account_id !== undefined && input.account_id !== binding.accountId
      || input.robot_id !== undefined && input.robot_id !== binding.robotId
      || input.environment !== undefined && input.environment !== binding.environment
      || (V2_RUNTIME_OPS.has(input.op) && input.source_sha256 !== binding.sourceSha256)
      || (role === "broker_reader" && input.source_sha256 !== binding.readerSourceSha256)) {
    throw new Denied("ROLE_BINDING_DENIED");
  }
}
function commonV2(input, keys) {
  if (!exactKeys(input, keys) || input.environment !== ENVIRONMENT
      || !identifier(input.account_id) || !robotId(input.robot_id) || !SHA.test(input.source_sha256)) {
    throw new Denied("V2_REQUEST_SHAPE");
  }
  return {p_environment: input.environment, p_account_id: input.account_id,
    p_robot_id: input.robot_id, p_source_sha256: input.source_sha256};
}
export async function validateEvidence(input, nowMs = Date.now(), allowStale = false) {
  const args = commonV2(input, [...COMMON_V2, "evidence_id", "kind", "observed_at", "raw_sha256", "facts_sha256", "facts"]);
  const facts = input.facts;
  if (!identifier(input.evidence_id) || !["PRE_CLAIM", "TERMINAL"].includes(input.kind)
      || !instant(input.observed_at) || Date.parse(input.observed_at) > nowMs
      || (!allowStale && nowMs - Date.parse(input.observed_at) > 30_000)
      || !SHA.test(input.raw_sha256) || !SHA.test(input.facts_sha256)
      || !exactKeys(facts, FACT_KEYS) || !identifier(facts.command_id)
      || !au(facts.instrument) || !action(facts.action) || !quantity(facts.filled_quantity)
      || !quantity(facts.position_quantity) || facts.pending_order_count !== 0
      || !nullableId(facts.claim_id) || !nullableId(facts.order_id)
      || !["raw_account_sha256", "raw_orders_sha256", "raw_trades_sha256", "raw_positions_sha256"].every(k => SHA.test(facts[k]))) {
    throw new Denied("BROKER_EVIDENCE_SHAPE_OR_TIME");
  }
  if (input.kind === "PRE_CLAIM") {
    if (facts.claim_id !== null || facts.order_id !== null || facts.order_status !== "NONE" || facts.filled_quantity !== 0) {
      throw new Denied("PRE_CLAIM_EVIDENCE_DENIED");
    }
  } else if (!identifier(facts.claim_id) || !identifier(facts.order_id)
      || !["FILLED", "REJECTED", "CANCELED"].includes(facts.order_status)
      || facts.filled_quantity !== (facts.order_status === "FILLED" ? 1 : 0)) {
    throw new Denied("TERMINAL_ORDER_TRUTH_REQUIRED");
  }
  const parties = facts.reconciliation;
  if (!exactKeys(parties, ["broker", "execution", "ledger", "expected"])) throw new Denied("FOUR_WAY_RECONCILIATION_REQUIRED");
  for (const party of Object.values(parties)) {
    if (!exactKeys(party, BALANCE_KEYS)
        || !["cash_cents", "available_cents", "frozen_margin_cents"].every(k => Number.isSafeInteger(party[k]) && party[k] >= 0)
        || party.position_quantity !== facts.position_quantity || party.filled_quantity !== facts.filled_quantity) {
      throw new Denied("FOUR_WAY_RECONCILIATION_SHAPE");
    }
  }
  for (const key of ["cash_cents", "available_cents", "frozen_margin_cents"]) {
    const amounts = Object.values(parties).map(p => p[key]);
    if (Math.max(...amounts) - Math.min(...amounts) > 1) throw new Denied("FOUR_WAY_RECONCILIATION_MISMATCH");
  }
  const hashes = Object.fromEntries(["raw_account_sha256", "raw_orders_sha256", "raw_trades_sha256", "raw_positions_sha256"].map(k => [k, facts[k]]));
  if (await objectHash(hashes) !== input.raw_sha256 || await objectHash(facts) !== input.facts_sha256) {
    throw new Denied("BROKER_EVIDENCE_HASH_MISMATCH");
  }
  return {...args, p_evidence_id: input.evidence_id, p_kind: input.kind, p_observed_at: input.observed_at,
    p_raw_sha256: input.raw_sha256, p_facts_sha256: input.facts_sha256, p_facts: facts,
    p_facts_canonical: canonical(facts), p_raw_canonical: canonical(hashes)};
}
export function validateCoordinator(input) {
  let extras = [];
  if (input.op === "read_claim_v2") extras = ["command_id"];
  else if (input.op === "claim_order_v2") extras = ["command_id", "contract_hash", "action", "instrument", "position_origin_claim_id", "broker_evidence_id"];
  else if (input.op === "record_submit_attempt_v2") extras = ["claim_id"];
  else if (input.op === "record_terminal_v2") extras = ["claim_id", "broker_evidence_id"];
  else if (input.op === "freeze_account_v2") extras = ["claim_id", "reason_code"];
  const mutation = !["read_claim_v2", "read_account_state_v2"].includes(input.op);
  const args = commonV2(input, [...(mutation ? MUTATION_V2 : COMMON_V2), ...extras]);
  if (mutation) {
    if (!version(input.expected_version) || !SHA.test(input.ledger_root_hash)
        || !Number.isSafeInteger(input.ledger_sequence) || input.ledger_sequence < 1) throw new Denied("V2_VERSION_OR_ANCHOR_SHAPE");
    Object.assign(args, {p_expected_version: input.expected_version, p_ledger_root_hash: input.ledger_root_hash, p_ledger_sequence: input.ledger_sequence});
  }
  if (input.op === "claim_order_v2") {
    if (!identifier(input.command_id) || !SHA.test(input.contract_hash) || !action(input.action) || !au(input.instrument)
        || !identifier(input.broker_evidence_id) || !nullableId(input.position_origin_claim_id)
        || (input.action === "OPEN_LONG" && input.position_origin_claim_id !== null)
        || (input.action === "CLOSE_LONG" && !identifier(input.position_origin_claim_id))) throw new Denied("V2_CLAIM_SHAPE");
    Object.assign(args, {p_command_id: input.command_id, p_contract_hash: input.contract_hash,
      p_action: input.action, p_instrument: input.instrument, p_position_origin_claim_id: input.position_origin_claim_id,
      p_broker_evidence_id: input.broker_evidence_id});
  } else if (input.op === "read_claim_v2") {
    if (!identifier(input.command_id)) throw new Denied("V2_CLAIM_SHAPE");
    args.p_command_id = input.command_id;
  } else if (input.op !== "read_account_state_v2") {
    if (!nullableId(input.claim_id) || (input.op !== "freeze_account_v2" && !identifier(input.claim_id))) throw new Denied("V2_CLAIM_SHAPE");
    args.p_claim_id = input.claim_id;
    if (input.op === "record_terminal_v2") {
      if (!identifier(input.broker_evidence_id)) throw new Denied("V2_EVIDENCE_REFERENCE_REQUIRED");
      args.p_broker_evidence_id = input.broker_evidence_id;
    }
    if (input.op === "freeze_account_v2") {
      if (typeof input.reason_code !== "string" || !/^[A-Z][A-Z0-9_]{2,95}$/.test(input.reason_code)) throw new Denied("V2_FREEZE_REASON_SHAPE");
      args.p_reason_code = input.reason_code;
    }
  }
  return args;
}
export function validateCoordinatorReply(result, input, binding) {
  if (!result || result.source !== COORDINATOR_SOURCE || result.account_id !== binding.accountId
      || result.environment !== binding.environment || result.robot_id !== binding.robotId
      || result.source_sha256 !== binding.sourceSha256 || !version(result.version)
      || !["FLAT", "CLAIMED", "SUBMIT_ATTEMPTED", "HELD", "FROZEN"].includes(result.phase)
      || !quantity(result.position_quantity) || !nullableId(result.position_origin_claim_id)
      || !nullableId(result.pending_claim_id) || !nullableId(result.claim_id) || !nullableId(result.command_id)
      || !(result.freeze_reason === null || (typeof result.freeze_reason === "string" && /^[A-Z][A-Z0-9_]{2,95}$/.test(result.freeze_reason)))
      || (result.phase === "FLAT" && (result.position_quantity !== 0 || result.pending_claim_id !== null))
      || (result.phase === "HELD" && (result.position_quantity !== 1 || result.pending_claim_id !== null))
      || (["CLAIMED", "SUBMIT_ATTEMPTED"].includes(result.phase) && result.pending_claim_id === null)
      || (result.phase === "FROZEN" && result.freeze_reason === null)
      || ((result.position_quantity === 0) !== (result.position_origin_claim_id === null))
      || typeof result.claimed !== "boolean" || !Number.isSafeInteger(result.ledger_sequence) || result.ledger_sequence < 0
      || !(SHA.test(result.ledger_root_hash) || (result.ledger_sequence === 0 && result.ledger_root_hash === "0".repeat(64)))
      || !instant(result.updated_at) || typeof result.status !== "string"
      || (result.claimed && (!["claim_order_v2", "claim_linked_exit_v3"].includes(input.op) || result.status !== "CLAIMED"))
      || (input.command_id && result.command_id !== input.command_id)
      || (input.claim_id && result.claim_id !== input.claim_id)) throw new Denied("REMOTE_ACCOUNT_READBACK_INVALID");
  if (result.status === "CLAIMED" && input.op === "claim_linked_exit_v3"
      && (result.position_quantity !== 1 || result.position_origin_claim_id !== input.parent_claim_id
          || result.freeze_reason !== "LINKED_EXIT_PAIR_RECONCILIATION_REQUIRED")) throw new Denied("LINKED_FRESH_CLAIM_RELATION_MISMATCH");
  if (result.status === "PAIR_RECORDED" && input.op === "complete_linked_pair_v3"
      && (result.phase !== "FROZEN" || result.position_quantity !== 0 || result.pending_claim_id !== null
          || result.position_origin_claim_id !== null || result.freeze_reason !== "LINKED_EXIT_PAIR_RECONCILED_REVIEW_REQUIRED")) throw new Denied("LINKED_PAIR_FLAT_FREEZE_MISMATCH");
  return result;
}


// V3 admits exactly one reduction under an unresolved filled OPEN. Native
// order provenance is a different evidence class from four-party settlement.
const NATIVE_HASH_KEYS = ["order_binding_sha256", "raw_identity_sha256", "raw_account_sha256", "raw_orders_sha256", "raw_trades_sha256", "raw_positions_sha256"];
const NATIVE_KEYS = ["command_id", "claim_id", "instrument", "action", "order_id", "order_status", "filled_quantity", "position_quantity", "pending_order_count", "parent_claim_id", "parent_order_id", "reconciliation", ...NATIVE_HASH_KEYS];
const PAIR_BALANCE_KEYS = ["producer_id", "proof_sha256", "cash_cents", "available_cents", "frozen_margin_cents", "position_quantity", "open_filled_quantity", "close_filled_quantity", "parent_order_id", "child_order_id"];
export async function validateNativeEvidence(input, nowMs = Date.now(), allowStale = false) {
  const args = commonV2(input, [...COMMON_V2, "evidence_id", "kind", "observed_at", "facts_sha256", "facts"]);
  const f = input.facts;
  if (!identifier(input.evidence_id) || !["NATIVE_ORDER", "PAIRED_TERMINAL"].includes(input.kind)
      || !instant(input.observed_at) || Date.parse(input.observed_at) > nowMs
      || (!allowStale && nowMs - Date.parse(input.observed_at) > 30000)
      || !exactKeys(f, NATIVE_KEYS) || !identifier(f.command_id) || !identifier(f.claim_id)
      || !au(f.instrument) || !action(f.action) || !identifier(f.order_id)
      || !["PENDING", "FILLED", "REJECTED", "CANCELED"].includes(f.order_status)
      || !quantity(f.filled_quantity) || !quantity(f.position_quantity) || !quantity(f.pending_order_count)
      || !NATIVE_HASH_KEYS.every(k => SHA.test(f[k]))
      || !SHA.test(input.facts_sha256) || await objectHash(f) !== input.facts_sha256
      || (f.order_status === "FILLED" && f.filled_quantity !== 1)
      || (["REJECTED", "CANCELED", "PENDING"].includes(f.order_status) && f.filled_quantity !== 0)
      || (f.order_status !== "PENDING" && f.pending_order_count !== 0)) throw new Denied("NATIVE_EVIDENCE_SHAPE_OR_HASH_DENIED");
  if (input.kind === "NATIVE_ORDER") {
    if (f.parent_claim_id !== null || f.parent_order_id !== null || f.reconciliation !== null) throw new Denied("NATIVE_EVIDENCE_CANNOT_CLAIM_RECONCILIATION");
  } else {
    if (f.action !== "CLOSE_LONG" || f.order_status !== "FILLED" || f.position_quantity !== 0 || f.pending_order_count !== 0
        || !identifier(f.parent_claim_id) || !identifier(f.parent_order_id) || f.parent_order_id === f.order_id
        || !exactKeys(f.reconciliation, ["broker", "execution", "ledger", "expected"])) throw new Denied("PAIRED_FOUR_WAY_REQUIRED");
    const parties = Object.values(f.reconciliation);
    if (new Set(parties.map(p => p?.producer_id)).size !== 4) throw new Denied("PAIRED_INDEPENDENT_PRODUCERS_REQUIRED");
    for (const p of parties) {
      if (!exactKeys(p, PAIR_BALANCE_KEYS) || !identifier(p.producer_id) || !SHA.test(p.proof_sha256)
          || p.position_quantity !== 0 || p.open_filled_quantity !== 1 || p.close_filled_quantity !== 1
          || p.parent_order_id !== f.parent_order_id || p.child_order_id !== f.order_id
          || !["cash_cents", "available_cents", "frozen_margin_cents"].every(k => version(p[k]))) throw new Denied("PAIRED_PARTY_SHAPE_DENIED");
    }
    for (const k of ["cash_cents", "available_cents", "frozen_margin_cents"]) {
      const a = parties.map(p => p[k]);
      if (Math.max(...a) - Math.min(...a) > 1) throw new Denied("PAIRED_FOUR_WAY_DRIFT");
    }
  }
  return {...args, p_evidence_id: input.evidence_id, p_kind: input.kind, p_observed_at: input.observed_at,
    p_facts_sha256: input.facts_sha256, p_facts: f, p_facts_canonical: canonical(f)};
}
export function validateLinkedOperation(input) {
  const claim = input.op === "claim_linked_exit_v3";
  const extras = claim ? ["command_id", "contract_hash", "parent_claim_id", "broker_evidence_id"] : ["claim_id", "broker_evidence_id"];
  const args = commonV2(input, [...MUTATION_V2, ...extras]);
  if (!version(input.expected_version) || !SHA.test(input.ledger_root_hash) || !Number.isSafeInteger(input.ledger_sequence) || input.ledger_sequence < 1
      || !identifier(input.broker_evidence_id)) throw new Denied("LINKED_REFERENCE_DENIED");
  Object.assign(args, {p_expected_version: input.expected_version, p_ledger_root_hash: input.ledger_root_hash,
    p_ledger_sequence: input.ledger_sequence, p_broker_evidence_id: input.broker_evidence_id});
  if (claim) {
    if (!identifier(input.command_id) || !identifier(input.parent_claim_id) || !SHA.test(input.contract_hash)) throw new Denied("LINKED_CLAIM_SHAPE_DENIED");
    Object.assign(args, {p_command_id: input.command_id, p_parent_claim_id: input.parent_claim_id, p_contract_hash: input.contract_hash});
  } else {
    if (!identifier(input.claim_id)) throw new Denied("LINKED_CLAIM_SHAPE_DENIED");
    args.p_claim_id = input.claim_id;
  }
  return args;
}
