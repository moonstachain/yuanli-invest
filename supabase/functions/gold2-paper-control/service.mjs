import {
  Denied, authenticate, canonical, prepareOperation, readBounded, signalProof,
  assertRoleBinding, validateEvidence, validateNativeEvidence, validateCoordinatorReply, V2_RUNTIME_OPS,
} from "./core.mjs";
import {ADMISSION_OPS, handleAdmission} from './admission-v4.mjs';

const decoder = new TextDecoder("utf-8", {fatal: true});

function response(status, payload) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {"content-type": "application/json; charset=utf-8", "cache-control": "no-store"},
  });
}

function same(a, b) { return canonical(a) === canonical(b); }

// rpc(name, args) must use only a server-held Supabase secret. A rejected or
// timed-out write is not retried here: its commit state may be unknowable.
export async function handleRequest(request, {enabled, claimEnabled = false, signalKey, runtimeKey, readerKey, binding, controlSigning,
                                              rpc, now = () => Date.now()}) {
  if (!enabled || !signalKey || !runtimeKey || !readerKey
      || new Set([signalKey, runtimeKey, readerKey]).size !== 3 || typeof rpc !== "function") {
    return response(503, {status: "SERVICE_DISABLED"});
  }
  try {
    const bytes = await readBounded(request);
    const role = await authenticate(request, bytes, {signal: signalKey, runtime: runtimeKey, reader: readerKey}, now());
    let input;
    try { input = JSON.parse(decoder.decode(bytes)); }
    catch { throw new Denied("INVALID_JSON"); }
    assertRoleBinding(input, role, binding);
    if (ADMISSION_OPS.has(input.op)) {
      const result = await handleAdmission(input, role, {binding,rpc,controlSigning,now});
      return response(result.httpStatus,result.payload);
    }
    const [name, args] = await prepareOperation(input, role, now());
    // V1 command-only claims can never be re-enabled by configuration.
    if (input.op === "claim_order") {
      return response(503, {status: "CLAIM_DISABLED_ACCOUNT_SERIALIZATION_PENDING"});
    }
    if (["claim_order_v2", "claim_linked_exit_v3"].includes(input.op) && claimEnabled !== true) {
      return response(503, {status: "CLAIM_DISABLED_ACCOUNT_SERIALIZATION_PENDING"});
    }
    const result = await rpc(name, args);
    if (input.op === "read_broker_evidence_v2" && result === null) return response(404, {status: "EVIDENCE_NOT_FOUND"});
    if (result === null || typeof result !== "object" || Array.isArray(result)) {
      return response(503, {status: "UNKNOWN_NO_RETRY"});
    }
    if (input.op === "anchor_signal" || input.op === "read_signal") {
      const readback = input.op === "read_signal" ? result : await rpc(
        "gold2_paper_read_signal_v1", {p_registry_id: args.p_registry_id, p_record_id: args.p_record_id});
      if (!readback || readback.record_sha256 !== (input.op === "anchor_signal" ? args.p_record_sha256 : readback.record_sha256)
          || readback.registry_root_sha256 !== (input.op === "anchor_signal" ? args.p_registry_root_sha256 : readback.registry_root_sha256)
          || readback.registry_id !== args.p_registry_id || readback.record_id !== args.p_record_id
          || (input.op === "anchor_signal" && !same(readback.record, args.p_record))) {
        return response(503, {status: "UNKNOWN_NO_RETRY"});
      }
      try {
        return response(200, await signalProof(readback, new Date(now()).toISOString()));
      } catch {
        return response(503, {status: "UNKNOWN_NO_RETRY"});
      }
    }
    if (input.op === "append_ledger") {
      const head = await rpc("gold2_paper_read_ledger_v1", {
        p_account_id: args.p_account_id, p_robot_id: args.p_robot_id,
      });
      if (!head || head.root_hash !== args.p_root_hash || head.last_sequence !== args.p_events.length
          || head.account_id !== args.p_account_id || head.robot_id !== args.p_robot_id
          || head.environment !== "SIMNOW_FIRST_NORMAL"
          || result.source !== "external_append_only_ledger" || result.accepted !== true
          || result.root_hash !== head.root_hash || result.last_sequence !== head.last_sequence) {
        return response(503, {status: "UNKNOWN_NO_RETRY"});
      }
      return response(200, result);
    }
    if (V2_RUNTIME_OPS.has(input.op)) {
      try { validateCoordinatorReply(result, input, binding); }
      catch { return response(503, {status: "UNKNOWN_NO_RETRY"}); }
      if (!["read_account_state_v2", "read_claim_v2"].includes(input.op)) {
        const state = await rpc("gold2_paper_read_account_state_v2", {
          p_environment: binding.environment, p_account_id: binding.accountId,
          p_robot_id: binding.robotId, p_source_sha256: binding.sourceSha256,
        });
        try { validateCoordinatorReply(state, {op: "read_account_state_v2"}, binding); }
        catch { return response(503, {status: "UNKNOWN_NO_RETRY"}); }
        for (const key of ["version", "phase", "pending_claim_id", "position_quantity", "position_origin_claim_id",
          "ledger_root_hash", "ledger_sequence", "freeze_reason"]) {
          if (result[key] !== state[key]) return response(503, {status: "UNKNOWN_NO_RETRY"});
        }
        if (result.claimed && (state.pending_claim_id !== result.claim_id || state.phase !== "CLAIMED"
            || result.version !== input.expected_version + 1)) return response(503, {status: "UNKNOWN_NO_RETRY"});
      }
      const ok = ["CLAIMED", "ACCOUNT_READ", "CLAIM_READ", "SUBMIT_RECORDED", "TERMINAL_RECORDED", "PAIR_RECORDED", "FROZEN"].includes(result.status);
      return response(ok ? 200 : 409, result);
    }
    if (["ingest_native_evidence_v3", "read_native_evidence_v3"].includes(input.op)) {
      const readback = input.op === "read_native_evidence_v3" ? result : await rpc("gold2_paper_read_native_evidence_v3", {
        p_environment: input.environment, p_account_id: input.account_id, p_robot_id: input.robot_id,
        p_source_sha256: input.source_sha256, p_evidence_id: input.evidence_id});
      if (!readback || readback.environment !== input.environment || readback.account_id !== input.account_id
          || readback.robot_id !== input.robot_id || readback.source_sha256 !== input.source_sha256
          || readback.evidence_id !== input.evidence_id || !Number.isFinite(Date.parse(readback.received_at))
          || Date.parse(readback.observed_at) > Date.parse(readback.received_at) || Date.parse(readback.received_at) > now()) {
        return response(503, {status: "UNKNOWN_NO_RETRY"});
      }
      try {
        await validateNativeEvidence({op: "ingest_native_evidence_v3", environment: readback.environment,
          account_id: readback.account_id, robot_id: readback.robot_id, source_sha256: readback.source_sha256,
          evidence_id: readback.evidence_id, kind: readback.kind, observed_at: readback.observed_at,
          facts_sha256: readback.facts_sha256, facts: readback.facts}, now(), input.op === "read_native_evidence_v3");
      } catch { return response(503, {status: "UNKNOWN_NO_RETRY"}); }
      if (input.op === "ingest_native_evidence_v3" && (readback.facts_sha256 !== input.facts_sha256
          || readback.kind !== input.kind || !same(readback.facts, input.facts))) return response(503, {status: "UNKNOWN_NO_RETRY"});
      return response(200, {...readback, source: "bound_broker_reader_evidence_v3",
        status: input.op === "ingest_native_evidence_v3" ? "EVIDENCE_RECORDED" : "EVIDENCE_READ",
        verified_at: new Date(now()).toISOString()});
    }
    if (input.op === "read_broker_evidence_v2") {
      if (result.environment !== input.environment || result.account_id !== input.account_id
          || result.robot_id !== input.robot_id || result.source_sha256 !== input.source_sha256
          || result.evidence_id !== input.evidence_id || !Number.isFinite(Date.parse(result.received_at))
          || Date.parse(result.observed_at) > Date.parse(result.received_at)
          || Date.parse(result.received_at) > now()) return response(503, {status: "UNKNOWN_NO_RETRY"});
      try {
        await validateEvidence({op: "ingest_broker_evidence_v2", environment: result.environment,
          account_id: result.account_id, robot_id: result.robot_id, source_sha256: result.source_sha256,
          evidence_id: result.evidence_id, kind: result.kind, observed_at: result.observed_at,
          raw_sha256: result.raw_sha256, facts_sha256: result.facts_sha256, facts: result.facts}, now(), true);
      } catch { return response(503, {status: "UNKNOWN_NO_RETRY"}); }
      return response(200, {...result, source: "bound_broker_reader_evidence_v2", status: "EVIDENCE_READ",
        verified_at: new Date(now()).toISOString()});
    }
    if (input.op === "ingest_broker_evidence_v2") {
      const facts = await rpc("gold2_paper_read_broker_evidence_v2", {
        p_environment: args.p_environment, p_account_id: args.p_account_id,
        p_robot_id: args.p_robot_id, p_source_sha256: args.p_source_sha256, p_evidence_id: args.p_evidence_id,
      });
      if (result.source !== "bound_broker_reader_evidence_v2" || result.status !== "EVIDENCE_RECORDED"
          || result.evidence_id !== args.p_evidence_id || result.facts_sha256 !== args.p_facts_sha256
          || !facts || facts.evidence_id !== args.p_evidence_id || facts.facts_sha256 !== args.p_facts_sha256
          || facts.raw_sha256 !== args.p_raw_sha256 || facts.account_id !== args.p_account_id
          || facts.robot_id !== args.p_robot_id || facts.environment !== args.p_environment
          || facts.source_sha256 !== args.p_source_sha256 || !same(facts.facts, args.p_facts)) {
        return response(503, {status: "UNKNOWN_NO_RETRY"});
      }
      return response(200, result);
    }
    if (input.op === "read_claim" && (result.account_id !== binding.accountId || result.robot_id !== binding.robotId
        || result.environment !== binding.environment)) throw new Denied("ROLE_BINDING_DENIED");
    return response(200, result);
  } catch (error) {
    if (error instanceof Denied) {
      const status = error.code === "AUTH_DENIED" || error.code === "REQUEST_METHOD_OR_TYPE" ? 401 : 400;
      return response(status, {status: "DENIED", reason: error.code});
    }
    // Includes network timeout, PostgREST 5xx, malformed reply and ambiguous
    // commit. The client must freeze and perform separate readback.
    return response(503, {status: "UNKNOWN_NO_RETRY"});
  }
}
