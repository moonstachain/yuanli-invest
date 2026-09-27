// Isolated PostgreSQL protocol checks only; no broker/remote credential/network.
import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
if (!process.env.GOLD2_PGLITE_MODULE) throw new Error('GOLD2_PGLITE_MODULE_REQUIRED');
const {PGlite}=await import(process.env.GOLD2_PGLITE_MODULE);const db=new PGlite();
try {
 await db.exec('create role anon; create role authenticated; create role service_role bypassrls;');
 for(const name of ['20260925072235_gold2_paper_private_receipts.sql','20260926081247_gold2_account_coordinator_v2.sql','20260926113459_gold2_linked_protective_exit_v3.sql']) await db.exec(await readFile(new URL('../supabase/migrations/'+name,import.meta.url),'utf8'));
 const result=await db.exec(await readFile(new URL('./gold2_linked_protective_sql_probe_v3.sql',import.meta.url),'utf8'));
 const proof=result.flatMap(r=>r.rows??[]).find(r=>r.result?.status==='GOLD2_LINKED_SQL_ROLLBACK_PASS').result;
 assert.equal(proof.passed,true);assert.ok(proof.checks>=24);
 const counts=(await db.query('select (select count(*) from gold2_paper.native_evidence_v3) as native_facts,(select count(*) from gold2_paper.linked_exits_v3) as linked_claims,(select count(*) from gold2_paper.runtime_bindings) as bindings')).rows[0];
 assert.deepEqual(counts,{native_facts:0,linked_claims:0,bindings:0});
 console.log(JSON.stringify({...proof,after_rollback:counts}));
}finally{await db.close();}
