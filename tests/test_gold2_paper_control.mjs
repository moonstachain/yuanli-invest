import assert from "node:assert/strict";
import {test} from "node:test";
import {canonical, objectHash, sha256, validateLedger, validateSignal} from "../supabase/functions/gold2-paper-control/core.mjs";
import {handleRequest} from "../supabase/functions/gold2-paper-control/service.mjs";

const SIGNAL_KEY = "signal-only-key-material-32-characters-minimum";
const RUNTIME_KEY = "runtime-only-key-material-32-characters-minimum";
const READER_KEY = "reader-only-key-material-32-characters-minimum";
const BINDING = {environment: "SIMNOW_FIRST_NORMAL", accountId: "SIMNOW-ACCOUNT-1", robotId: 19,
  sourceSha256: "sha256:" + "a".repeat(64), readerSourceSha256: "sha256:" + "b".repeat(64)};
const NOW = Date.parse("2026-09-25T00:30:20.000Z");
const URL = "https://example.supabase.co/functions/v1/gold2-paper-control";
const HASH6 = "sha256:" + "6".repeat(64);

const record = {
  registry_id: "GOLD2-AU-PREREG-LOCAL",
  record_id: "GOLD2-AU-SIGREG-ABCDEFGHIJKLMNOPQRSTUVWX",
  source_ref: "LOCAL_SQLITE_PREREGISTRATION_CANDIDATE",
  recorded_at: "2026-09-25T08:30:12+08:00",
  decision_at: "2026-09-25T08:30:00+08:00",
  signal_id: "sha256:" + "1".repeat(64),
  signal_sha256: "sha256:" + "2".repeat(64),
  frozen_dataset_sha256: "sha256:" + "3".repeat(64),
  parameters_sha256: "sha256:" + "4".repeat(64),
  forward_decision_id: "GOLD2-AU-DECISION-1",
  forward_decision_sha256: "sha256:" + "5".repeat(64),
  outcome_contracts: [
    {horizon_trading_days: 5, session_date: "2026-10-09", decision_id: "GOLD2-AU-DECISION-1", outcome_contract_id: "GOLD2-AU-OUT-AAAAAAAA"},
    {horizon_trading_days: 20, session_date: "2026-10-30", decision_id: "GOLD2-AU-DECISION-1", outcome_contract_id: "GOLD2-AU-OUT-BBBBBBBB"},
  ],
};
const recordHash = "sha256:de884a95a20e57e5b19043b31894bcec7735359122219c4125aafff39b52b00c";
const event = {
  sequence: 1,
  kind: "ActionAdmitted",
  command_id: "CMD-GOLD2-12345678",
  at: "2026-09-25T00:30:12+00:00",
  data: {contract_hash: HASH6},
  previous_hash: "0".repeat(64),
  event_hash: "sha256:e414b1102dde33b9dcf1c3bda8dca9ec299485b19866690ba902ddad30a06b48",
};

async function signed(payload, role = "signal", options = {}) {
  const key = options.key ?? (role === "signal" ? SIGNAL_KEY : role === "broker_reader" ? READER_KEY : RUNTIME_KEY);
  const body = JSON.stringify(payload);
  const timestamp = options.timestamp ?? new Date(NOW).toISOString();
  const material = "GOLD2-PAPER-V1\nPOST\n/functions/v1/gold2-paper-control\n"
    + timestamp + "\n" + await sha256(body);
  const hmacKey = await crypto.subtle.importKey("raw", new TextEncoder().encode(key),
    {name: "HMAC", hash: "SHA-256"}, false, ["sign"]);
  const mac = await crypto.subtle.sign("HMAC", hmacKey, new TextEncoder().encode(material));
  const signature = Array.from(new Uint8Array(mac), b => b.toString(16).padStart(2, "0")).join("");
  return new Request(URL, {method: "POST", headers: {
    "content-type": "application/json", "x-gold2-role": role,
    "x-gold2-timestamp": timestamp,
    "x-gold2-signature": "sha256=" + (options.tamper ? "0".repeat(64) : signature),
  }, body});
}

function deps(rpc) { return {enabled: true, claimEnabled: true,
  signalKey: SIGNAL_KEY, runtimeKey: RUNTIME_KEY, readerKey: READER_KEY, binding: BINDING,
  rpc, now: () => NOW}; }

test("Python canonical GOLD2 signal and PaperLedger hashes match the Edge verifier", async () => {
  assert.equal(await objectHash(record), recordHash);
  assert.equal(await objectHash(Object.fromEntries(Object.entries(event).filter(([k]) => k !== "event_hash"))), event.event_hash);
  assert.equal((await validateSignal({op: "anchor_signal", record, record_sha256: recordHash,
    registry_root_sha256: "sha256:" + "7".repeat(64)})).p_record_id, record.record_id);
  assert.equal((await validateLedger({op: "append_ledger", account_id: "SIMNOW-ACCOUNT-1", robot_id: 19,
    events: [event], root_hash: event.event_hash})).p_root_hash, event.event_hash);
  await assert.rejects(validateLedger({op: "append_ledger", account_id: "SIMNOW-ACCOUNT-1", robot_id: 19,
    events: [{...event, data: {contract_hash: "sha256:" + "8".repeat(64)}}], root_hash: event.event_hash}),
    {code: "LEDGER_EVENT_HASH_MISMATCH"});
  assert.throws(() => canonical({value: 1.5}), {code: "NON_INTEGER_JSON_NUMBER"});
});

test("disabled, tampered and wrong-scope requests do not reach the database", async () => {
  let calls = 0;
  const rpc = async () => { calls++; throw new Error("unexpected"); };
  const payload = {op: "read_signal", registry_id: record.registry_id, record_id: record.record_id};
  assert.equal((await handleRequest(await signed(payload), {...deps(rpc), enabled: false})).status, 503);
  assert.equal((await handleRequest(await signed(payload, "signal", {tamper: true}), deps(rpc))).status, 401);
  assert.equal((await handleRequest(await signed(payload, "runtime"), deps(rpc))).status, 400);
  assert.equal((await handleRequest(await signed(payload, "signal", {
    timestamp: "2026-09-25T00:29:00.000Z"}), deps(rpc))).status, 401);
  assert.equal(calls, 0);
});

test("signal anchor requires independently read-back exact record and stable proof", async () => {
  const stored = {registry_id: record.registry_id, record_id: record.record_id,
    record_sha256: recordHash, registry_root_sha256: "sha256:" + "7".repeat(64),
    decision_at: record.decision_at, recorded_at: record.recorded_at,
    anchor_received_at: "2026-09-25T00:30:15+00:00", record};
  let reads = 0;
  const rpc = async (name) => name === "gold2_paper_anchor_signal_v1"
    ? {status: "ANCHORED", ...stored} : (reads++, stored);
  const anchorPayload = {op: "anchor_signal", record, record_sha256: recordHash,
    registry_root_sha256: stored.registry_root_sha256};
  const anchored = await handleRequest(await signed(anchorPayload), deps(rpc));
  assert.equal(anchored.status, 200);
  const proof = await anchored.json();
  assert.equal(proof.status, "VERIFIED_EXTERNAL_TIME_AND_INCLUSION");
  const read = await handleRequest(await signed({op: "read_signal", registry_id: record.registry_id,
    record_id: record.record_id}), deps(rpc));
  assert.equal((await read.json()).proof_sha256, proof.proof_sha256);
  assert.equal(reads, 2);
  const unknown = await handleRequest(await signed(anchorPayload), deps(async name =>
    name === "gold2_paper_anchor_signal_v1" ? {status: "ANCHORED"} : {...stored, record_sha256: HASH6}));
  assert.equal((await unknown.json()).status, "UNKNOWN_NO_RETRY");
});

test("candidate Edge wiring disables order claims until account-wide serialization exists", async () => {
  const payload = {op: "claim_order", command_id: "CMD-GOLD2-12345678", account_id: "SIMNOW-ACCOUNT-1",
    robot_id: 19, contract_hash: HASH6};
  let calls = 0;
  const result = await handleRequest(await signed(payload, "runtime"),
    {...deps(async () => {calls++;}), claimEnabled: false});
  assert.equal(result.status, 503);
  assert.equal((await result.json()).status, "CLAIM_DISABLED_ACCOUNT_SERIALIZATION_PENDING");
  assert.equal(calls, 0);
});

test("ledger append requires remote head readback; divergent head stays UNKNOWN", async () => {
  const payload = {op: "append_ledger", account_id: "SIMNOW-ACCOUNT-1", robot_id: 19,
    events: [event], root_hash: event.event_hash};
  const result = await handleRequest(await signed(payload, "runtime"), deps(async name =>
    name === "gold2_paper_append_ledger_v1"
      ? {source: "external_append_only_ledger", accepted: true, root_hash: event.event_hash, last_sequence: 1}
      : {account_id: payload.account_id, robot_id: 19, root_hash: HASH6, last_sequence: 1}));
  assert.equal(result.status, 503);
  assert.equal((await result.json()).status, "UNKNOWN_NO_RETRY");
});

test("matching append and independently read-back head produce anchor receipt", async () => {
  const payload = {op: "append_ledger", account_id: "SIMNOW-ACCOUNT-1", robot_id: 19,
    events: [event], root_hash: event.event_hash};
  const result = await handleRequest(await signed(payload, "runtime"), deps(async name =>
    name === "gold2_paper_append_ledger_v1"
      ? {source: "external_append_only_ledger", accepted: true, account_id: payload.account_id,
         robot_id: 19, root_hash: event.event_hash, last_sequence: 1}
      : {account_id: payload.account_id, robot_id: 19, environment: "SIMNOW_FIRST_NORMAL",
         root_hash: event.event_hash, last_sequence: 1}));
  assert.equal(result.status, 200);
  assert.equal((await result.json()).root_hash, event.event_hash);
});

const HASH_A = BINDING.sourceSha256;
const COMMON = {environment: BINDING.environment, account_id: BINDING.accountId,
  robot_id: BINDING.robotId, source_sha256: HASH_A};
const CLAIM_ID = "CLM-01234567890123456789012345678901";
function claimRequest(changes = {}) {
  return {op: "claim_order_v2", ...COMMON, command_id: "CMD-GOLD2-12345678", contract_hash: HASH6,
    action: "OPEN_LONG", instrument: "au2612", position_origin_claim_id: null,
    broker_evidence_id: "EVIDENCE-PRE-1", expected_version: 0, ledger_root_hash: HASH6, ledger_sequence: 1, ...changes};
}
function accountReply(changes = {}) {
  return {source: "external_account_coordinator_v2", status: "ACCOUNT_READ", ...COMMON,
    claimed: false, version: 1, phase: "CLAIMED", pending_claim_id: CLAIM_ID, claim_id: CLAIM_ID,
    command_id: "CMD-GOLD2-12345678", position_quantity: 0, position_origin_claim_id: null,
    ledger_root_hash: HASH6, ledger_sequence: 1, freeze_reason: null,
    updated_at: new Date(NOW).toISOString(), ...changes};
}
async function evidence(changes = {}, factChanges = {}) {
  const balances = {cash_cents: 500_000_000, available_cents: 500_000_000,
    frozen_margin_cents: 0, position_quantity: 0, filled_quantity: 0};
  const facts = {command_id: "CMD-GOLD2-12345678", claim_id: null, instrument: "au2612", action: "OPEN_LONG",
    order_id: null, order_status: "NONE", filled_quantity: 0, position_quantity: 0, pending_order_count: 0,
    reconciliation: Object.fromEntries(["broker", "execution", "ledger", "expected"].map(k => [k, {...balances}])),
    raw_account_sha256: HASH6, raw_orders_sha256: HASH6, raw_trades_sha256: HASH6, raw_positions_sha256: HASH6,
    ...factChanges};
  const hashes = Object.fromEntries(["raw_account_sha256", "raw_orders_sha256", "raw_trades_sha256", "raw_positions_sha256"].map(k => [k, facts[k]]));
  return {op: "ingest_broker_evidence_v2", ...COMMON, source_sha256: BINDING.readerSourceSha256,
    evidence_id: "EVIDENCE-PRE-1", kind: "PRE_CLAIM", observed_at: new Date(NOW - 1000).toISOString(),
    raw_sha256: await objectHash(hashes), facts_sha256: await objectHash(facts), facts, ...changes};
}

for (const change of [{account_id: "OTHER-ACCOUNT"}, {robot_id: 20}, {environment: "LIVE"}, {source_sha256: HASH6}]) {
  test("runtime key cannot change its bound identity " + JSON.stringify(change), async () => {
    let calls = 0;
    const res = await handleRequest(await signed(claimRequest(change), "runtime"), deps(async () => {calls++;}));
    assert.equal(res.status, 400); assert.equal((await res.json()).reason, "ROLE_BINDING_DENIED"); assert.equal(calls, 0);
  });
}
test("V1 claim is denied even if claimEnabled is true", async () => {
  let calls = 0;
  const res = await handleRequest(await signed({op: "claim_order", account_id: BINDING.accountId,
    robot_id: 19, command_id: "CMD-GOLD2-12345678", contract_hash: HASH6}, "runtime"), deps(async () => {calls++;}));
  assert.equal(res.status, 503); assert.equal(calls, 0);
});
test("claimEnabled defaults false for V2 as well", async () => {
  let calls = 0; const options = deps(async () => {calls++;}); delete options.claimEnabled;
  const res = await handleRequest(await signed(claimRequest(), "runtime"), options);
  assert.equal(res.status, 503); assert.equal(calls, 0);
});
test("fresh claim requires independent account readback before one-shot permission", async () => {
  const names = [];
  const res = await handleRequest(await signed(claimRequest(), "runtime"), deps(async name => {
    names.push(name); return name.endsWith("claim_order_v2") ? accountReply({status: "CLAIMED", claimed: true}) : accountReply();
  }));
  assert.equal(res.status, 200); assert.equal((await res.json()).claimed, true);
  assert.deepEqual(names, ["gold2_paper_claim_order_v2", "gold2_paper_read_account_state_v2"]);
});
test("repeated command returns no submit authority even with matching account readback", async () => {
  const res = await handleRequest(await signed(claimRequest(), "runtime"), deps(async name =>
    accountReply({status: name.endsWith("claim_order_v2") ? "ALREADY_CLAIMED" : "ACCOUNT_READ"})));
  assert.equal(res.status, 409); assert.equal((await res.json()).claimed, false);
});
test("response lost after committed claim is UNKNOWN; separate read never reclaims", async () => {
  let writes = 0; let committed;
  const rpc = async name => {
    if (name.endsWith("claim_order_v2")) {writes++; committed = accountReply(); throw new Error("response lost after commit");}
    return committed;
  };
  const first = await handleRequest(await signed(claimRequest(), "runtime"), deps(rpc));
  assert.equal(first.status, 503); assert.equal((await first.json()).status, "UNKNOWN_NO_RETRY");
  const read = await handleRequest(await signed({op: "read_account_state_v2", ...COMMON}, "runtime"), deps(rpc));
  assert.equal(read.status, 200); assert.equal((await read.json()).claimed, false); assert.equal(writes, 1);
});
for (const change of [{version: 3}, {phase: "SUBMIT_ATTEMPTED"}, {pending_claim_id: null}, {ledger_root_hash: HASH_A},
  {position_quantity: 1}, {freeze_reason: "BROKER_UNKNOWN"}]) {
  test("divergent post-claim account state revokes fresh authority " + JSON.stringify(change), async () => {
    const res = await handleRequest(await signed(claimRequest(), "runtime"), deps(async name =>
      name.endsWith("claim_order_v2") ? accountReply({status: "CLAIMED", claimed: true}) : accountReply(change)));
    assert.equal(res.status, 503); assert.equal((await res.json()).status, "UNKNOWN_NO_RETRY");
  });
}
test("concurrent requests receive at most one fresh permission from atomic coordinator", async () => {
  // This is an Edge response contract test. Real row-lock SQL is separately
  // exercised by the rollback probe; this in-memory oracle is not CTP proof.
  let selected = false;
  const rpc = async name => {
    if (name.endsWith("claim_order_v2")) {
      const fresh = !selected; selected = true;
      return accountReply({status: fresh ? "CLAIMED" : "ALREADY_CLAIMED", claimed: fresh});
    }
    return accountReply();
  };
  const replies = await Promise.all(Array.from({length: 12}, async () =>
    (await handleRequest(await signed(claimRequest(), "runtime"), deps(rpc))).json()));
  assert.equal(replies.filter(r => r.claimed === true).length, 1);
  assert.equal(replies.filter(r => r.status === "ALREADY_CLAIMED" && r.claimed === false).length, 11);
});
test("caller MATCHED dictionary cannot release an account slot", async () => {
  let calls = 0;
  const res = await handleRequest(await signed({op: "record_terminal_v2", ...COMMON, claim_id: CLAIM_ID,
    expected_version: 2, ledger_root_hash: HASH6, ledger_sequence: 3, broker_evidence_id: "EVIDENCE-TERMINAL-1",
    reconciliation: {status: "MATCHED"}}, "runtime"), deps(async () => {calls++;}));
  assert.equal(res.status, 400); assert.equal(calls, 0);
});
test("runtime principal cannot ingest reader facts even when correctly hashed", async () => {
  let calls = 0; const res = await handleRequest(await signed(await evidence(), "runtime"), deps(async () => {calls++;}));
  assert.equal(res.status, 400); assert.equal(calls, 0);
});
test("reader principal cannot claim or append an execution ledger", async () => {
  for (const payload of [claimRequest(), {op: "append_ledger", account_id: BINDING.accountId, robot_id: 19, events: [event], root_hash: event.event_hash}]) {
    let calls = 0; const res = await handleRequest(await signed(payload, "broker_reader"), deps(async () => {calls++;}));
    assert.equal(res.status, 400); assert.equal(calls, 0);
  }
});
test("reader HMAC cannot reuse runtime key material", async () => {
  const res = await handleRequest(await signed(await evidence(), "broker_reader", {key: RUNTIME_KEY}), deps(async () => null));
  assert.equal(res.status, 401);
});
test("bound reader facts require exact independent persisted readback", async () => {
  const payload = await evidence();
  const res = await handleRequest(await signed(payload, "broker_reader"), deps(async name =>
    name.endsWith("ingest_broker_evidence_v2") ? {source: "bound_broker_reader_evidence_v2", status: "EVIDENCE_RECORDED",
      evidence_id: payload.evidence_id, facts_sha256: payload.facts_sha256, raw_sha256: payload.raw_sha256, received_at: new Date(NOW).toISOString()}
    : {...payload}));
  assert.equal(res.status, 200); assert.equal((await res.json()).status, "EVIDENCE_RECORDED");
});
for (const transform of [
  p => ({...p, observed_at: new Date(NOW + 1).toISOString()}),
  p => ({...p, observed_at: new Date(NOW - 30_001).toISOString()}),
  p => ({...p, facts_sha256: HASH_A}),
  p => ({...p, raw_sha256: HASH_A}),
  p => ({...p, source_sha256: HASH_A}),
  p => ({...p, facts: {...p.facts, pending_order_count: 1}}),
  p => ({...p, facts: {...p.facts, reconciliation: {status: "MATCHED"}}}),
  p => ({...p, kind: "TERMINAL"}),
]) {
  test("invalid reader facts cannot reach SQL " + transform.toString(), async () => {
    let calls = 0;
    const res = await handleRequest(await signed(transform(await evidence()), "broker_reader"), deps(async () => {calls++;}));
    assert.equal(res.status, 400); assert.equal(calls, 0);
  });
}
for (const field of ["cash_cents", "available_cents", "frozen_margin_cents", "position_quantity", "filled_quantity"]) {
  test("four-way reader facts reject drift in " + field, async () => {
    const payload = await evidence(); payload.facts.reconciliation.expected[field] += 2;
    payload.facts_sha256 = await objectHash(payload.facts);
    let calls = 0; const res = await handleRequest(await signed(payload, "broker_reader"), deps(async () => {calls++;}));
    assert.equal(res.status, 400); assert.equal(calls, 0);
  });
}
test("terminal without explicit broker order identity cannot become admissible evidence", async () => {
  const payload = await evidence({kind: "TERMINAL"}, {claim_id: CLAIM_ID, order_status: "REJECTED"});
  let calls = 0; const res = await handleRequest(await signed(payload, "broker_reader"), deps(async () => {calls++;}));
  assert.equal(res.status, 400); assert.equal(calls, 0);
});
test("OPEN requires null origin and CLOSE requires a confirmed origin", async () => {
  for (const change of [{position_origin_claim_id: CLAIM_ID}, {action: "CLOSE_LONG", position_origin_claim_id: null}]) {
    let calls = 0; const res = await handleRequest(await signed(claimRequest(change), "runtime"), deps(async () => {calls++;}));
    assert.equal(res.status, 400); assert.equal(calls, 0);
  }
});
test("stale version denial remains a denial rather than success", async () => {
  const res = await handleRequest(await signed(claimRequest(), "runtime"), deps(async name =>
    accountReply({status: name.endsWith("claim_order_v2") ? "VERSION_CONFLICT" : "ACCOUNT_READ"})));
  assert.equal(res.status, 409); assert.equal((await res.json()).status, "VERSION_CONFLICT");
});
test("readback never grants claim authority and accepts only the bound account", async () => {
  const input = {op: "read_account_state_v2", ...COMMON};
  const res = await handleRequest(await signed(input, "runtime"), deps(async () => accountReply({claimed: true, status: "CLAIMED"})));
  assert.equal(res.status, 503);
});
test("legacy read_claim cannot reveal another runtime account", async () => {
  const res = await handleRequest(await signed({op: "read_claim", command_id: "CMD-GOLD2-12345678"}, "runtime"), deps(async () =>
    ({account_id: "OTHER-ACCOUNT", robot_id: 19, environment: BINDING.environment})));
  assert.equal(res.status, 400); assert.equal((await res.json()).reason, "ROLE_BINDING_DENIED");
});
test("unknown reader write may be resolved only by separate readback", async () => {
  const payload = await evidence(); let writes = 0;
  const stored = {...payload, received_at: new Date(NOW).toISOString()}; delete stored.op;
  const rpc = async name => {
    if (name.endsWith("ingest_broker_evidence_v2")) {writes++; throw new Error("commit response lost");}
    return stored;
  };
  const write = await handleRequest(await signed(payload, "broker_reader"), deps(rpc));
  assert.equal(write.status, 503);
  const read = await handleRequest(await signed({op: "read_broker_evidence_v2", ...COMMON,
    source_sha256: BINDING.readerSourceSha256, evidence_id: payload.evidence_id}, "broker_reader"), deps(rpc));
  assert.equal(read.status, 200); assert.equal((await read.json()).status, "EVIDENCE_READ"); assert.equal(writes, 1);
});
test("historical evidence read does not refresh observed_at or license trading", async () => {
  const payload = await evidence({observed_at: new Date(NOW - 600_000).toISOString()});
  const stored = {...payload, received_at: new Date(NOW - 599_000).toISOString()}; delete stored.op;
  const read = await handleRequest(await signed({op: "read_broker_evidence_v2", ...COMMON,
    source_sha256: BINDING.readerSourceSha256, evidence_id: payload.evidence_id}, "broker_reader"), deps(async () => stored));
  assert.equal(read.status, 200); const body = await read.json(); assert.equal(body.observed_at, payload.observed_at);
  assert.equal(body.claimed, undefined);
});
test("reader read rejects corrupt stored facts and mismatched binding", async () => {
  const payload = await evidence();
  for (const changes of [{facts_sha256: HASH_A}, {robot_id: 20}, {received_at: new Date(NOW + 1).toISOString()}]) {
    const stored = {...payload, received_at: new Date(NOW).toISOString(), ...changes}; delete stored.op;
    const read = await handleRequest(await signed({op: "read_broker_evidence_v2", ...COMMON,
      source_sha256: BINDING.readerSourceSha256, evidence_id: payload.evidence_id}, "broker_reader"), deps(async () => stored));
    assert.equal(read.status, 503);
  }
});
test("reader read missing evidence is explicit and cannot trigger another write", async () => {
  let calls = 0; const payload = await evidence();
  const read = await handleRequest(await signed({op: "read_broker_evidence_v2", ...COMMON,
    source_sha256: BINDING.readerSourceSha256, evidence_id: payload.evidence_id}, "broker_reader"), deps(async () => {calls++; return null;}));
  assert.equal(read.status, 404); assert.equal(calls, 1);
});
test("shared role key configuration stays disabled rather than accepting role substitution", async () => {
  let calls = 0;
  const res = await handleRequest(await signed(claimRequest(), "runtime"), {...deps(async () => {calls++;}), readerKey: RUNTIME_KEY});
  assert.equal(res.status, 503); assert.equal((await res.json()).status, "SERVICE_DISABLED"); assert.equal(calls, 0);
});
