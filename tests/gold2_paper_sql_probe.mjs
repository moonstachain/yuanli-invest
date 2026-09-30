// Optional isolated in-memory PostgreSQL semantic probe. No cloud connection.
// GOLD2_PGLITE_MODULE must point to a locally installed pinned PGlite module.
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {fileURLToPath} from "node:url";

const modulePath = process.env.GOLD2_PGLITE_MODULE;
if (!modulePath) throw new Error("GOLD2_PGLITE_MODULE_REQUIRED");
const {PGlite} = await import(modulePath);
const migrationUrl = new URL("../supabase/migrations/20260925072235_gold2_paper_private_receipts.sql", import.meta.url);
const db = new PGlite();
try {
  await db.exec("create role anon; create role authenticated; create role service_role bypassrls;");
  await db.exec(await readFile(fileURLToPath(migrationUrl), "utf8"));
  const event = {
    sequence: 1, kind: "ActionAdmitted", command_id: "CMD-GOLD2-12345678",
    at: "2026-09-25T00:30:12+00:00",
    data: {contract_hash: "sha256:" + "6".repeat(64)},
    previous_hash: "0".repeat(64),
    event_hash: "sha256:e414b1102dde33b9dcf1c3bda8dca9ec299485b19866690ba902ddad30a06b48",
  };
  await db.exec("set role service_role");
  const claim = async hash => (await db.query(
    "select public.gold2_paper_claim_order_v1($1,$2,$3,$4) as result",
    [event.command_id, "SIMNOW-ACCOUNT-1", 19, hash])).rows[0].result;
  assert.equal((await claim(event.data.contract_hash)).status, "CLAIMED");
  assert.equal((await claim(event.data.contract_hash)).status, "ALREADY_CLAIMED");
  assert.equal((await claim("sha256:" + "7".repeat(64))).status, "CONFLICT");

  const append = async (events, root) => (await db.query(
    "select public.gold2_paper_append_ledger_v1($1,$2,$3::jsonb,$4) as result",
    ["SIMNOW-ACCOUNT-1", 19, JSON.stringify(events), root])).rows[0].result;
  assert.equal((await append([event], event.event_hash)).last_sequence, 1);
  assert.equal((await append([event], event.event_hash)).last_sequence, 1);
  await assert.rejects(append([{...event, data: {changed: true}}], event.event_hash),
    /GOLD2_LEDGER_PREFIX_DIVERGED/);
  const counts = (await db.query("select (select count(*) from gold2_paper.order_claims) as claims, "
    + "(select count(*) from gold2_paper.ledger_events) as events")).rows[0];
  assert.deepEqual(counts, {claims: 1, events: 1});
  await assert.rejects(db.query("select public.gold2_paper_anchor_signal_v1($1,$2,$3,$4,$5,$6,$7::jsonb)", [
    "GOLD2-AU-PREREG-LOCAL", "GOLD2-AU-SIGREG-PAST",
    "sha256:" + "1".repeat(64), "sha256:" + "2".repeat(64),
    "2025-09-25T08:30:00+08:00", "2025-09-25T08:30:10+08:00",
    JSON.stringify({registry_id: "GOLD2-AU-PREREG-LOCAL", record_id: "GOLD2-AU-SIGREG-PAST",
      decision_at: "2025-09-25T08:30:00+08:00", recorded_at: "2025-09-25T08:30:10+08:00"}),
  ]), /GOLD2_SIGNAL_LATE_OR_FUTURE/);
  await db.exec("reset role; set role anon");
  await assert.rejects(db.query("select public.gold2_paper_read_claim_v1($1)", [event.command_id]),
    /permission denied/);
  await assert.rejects(db.query("select * from gold2_paper.order_claims"), /permission denied/);
  await db.exec("reset role");
  await assert.rejects(db.query("update gold2_paper.ledger_events set event_hash = $1 where sequence = 1",
    ["sha256:" + "8".repeat(64)]), /GOLD2_HISTORY_APPEND_ONLY/);
  console.log(JSON.stringify({status: "GOLD2_PAPER_SQL_ISOLATED_PASS", claims: 1, events: 1,
    duplicate_claim_blocked: true, prefix_divergence_blocked: true,
    late_anchor_blocked: true, anon_blocked: true, mutation_blocked: true}));
} finally {
  await db.close();
}
