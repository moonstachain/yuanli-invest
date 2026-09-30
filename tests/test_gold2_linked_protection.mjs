import test from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {canonical, objectHash, sha256, prepareOperation, validateNativeEvidence, validateCoordinatorReply} from '../supabase/functions/gold2-paper-control/core.mjs';
import {handleRequest} from '../supabase/functions/gold2-paper-control/service.mjs';
if (!globalThis.crypto) Object.defineProperty(globalThis, "crypto", {value: webcrypto});
const NOW=Date.parse('2026-09-28T01:01:00Z');
const H='sha256:'+'f'.repeat(64), S='sha256:'+'a'.repeat(64), R='sha256:'+'b'.repeat(64);
const B={environment:'SIMNOW_FIRST_NORMAL',accountId:'PAPER-FIXTURE',robotId:19,sourceSha256:S,readerSourceSha256:R};
const C={environment:B.environment,account_id:B.accountId,robot_id:19,source_sha256:S};
const keys={signal:'signal-test-key-000000000000000000000',runtime:'runtime-test-key-0000000000000000000',broker_reader:'reader-test-key-00000000000000000000'};
function facts(){return {command_id:'OPEN-CMD',claim_id:'OPEN-CLM',instrument:'au2612',action:'OPEN_LONG',order_id:'OPEN-ORDER',order_status:'FILLED',filled_quantity:1,position_quantity:1,pending_order_count:0,parent_claim_id:null,parent_order_id:null,reconciliation:null,
  ...Object.fromEntries(['order_binding_sha256','raw_identity_sha256','raw_account_sha256','raw_orders_sha256','raw_trades_sha256','raw_positions_sha256'].map(k=>[k,H]))};}
function pair(){const f={...facts(),command_id:'CLOSE-CMD',claim_id:'CLOSE-CLM',order_id:'CLOSE-ORDER',action:'CLOSE_LONG',position_quantity:0,parent_claim_id:'OPEN-CLM',parent_order_id:'OPEN-ORDER'};
  f.reconciliation=Object.fromEntries(['broker','execution','ledger','expected'].map(p=>[p,{producer_id:'PRODUCER-'+p,proof_sha256:H,cash_cents:500000000,available_cents:500000000,frozen_margin_cents:0,position_quantity:0,open_filled_quantity:1,close_filled_quantity:1,parent_order_id:'OPEN-ORDER',child_order_id:'CLOSE-ORDER'}]));return f;}
async function evidence(f=facts(),kind='NATIVE_ORDER'){return {...C,source_sha256:R,op:'ingest_native_evidence_v3',evidence_id:'EVIDENCE-1',kind,observed_at:new Date(NOW).toISOString(),facts:f,facts_sha256:await objectHash(f)};}
const claim={...C,op:'claim_linked_exit_v3',expected_version:2,ledger_root_hash:H,ledger_sequence:6,command_id:'CLOSE-CMD',contract_hash:H,parent_claim_id:'OPEN-CLM',broker_evidence_id:'EVIDENCE-1'};
function state(extra={}){return {source:'external_account_coordinator_v2',status:'CLAIMED',claimed:true,...C,version:3,phase:'CLAIMED',pending_claim_id:'CLOSE-CLM',claim_id:'CLOSE-CLM',command_id:'CLOSE-CMD',position_quantity:1,position_origin_claim_id:'OPEN-CLM',ledger_root_hash:H,ledger_sequence:6,freeze_reason:'LINKED_EXIT_PAIR_RECONCILIATION_REQUIRED',updated_at:new Date(NOW).toISOString(),...extra};}
async function signed(input,role='runtime'){const body=canonical(input),timestamp=new Date(NOW).toISOString();const material='GOLD2-PAPER-V1\nPOST\n/functions/v1/gold2-paper-control\n'+timestamp+'\n'+await sha256(body);const k=await crypto.subtle.importKey('raw',new TextEncoder().encode(keys[role]),{name:'HMAC',hash:'SHA-256'},false,['sign']);const mac=await crypto.subtle.sign('HMAC',k,new TextEncoder().encode(material));return new Request('https://paper.example/functions/v1/gold2-paper-control',{method:'POST',headers:{'content-type':'application/json','x-gold2-role':role,'x-gold2-timestamp':timestamp,'x-gold2-signature':'sha256='+Buffer.from(mac).toString('hex')},body});}
function deps(rpc,extra={}){return {enabled:true,claimEnabled:true,signalKey:keys.signal,runtimeKey:keys.runtime,readerKey:keys.broker_reader,binding:B,rpc,now:()=>NOW,...extra};}

test('native parent fill has provenance but never fourway settlement',async()=>{const e=await evidence();assert.equal((await prepareOperation(e,'broker_reader',NOW))[0],'gold2_paper_ingest_native_evidence_v3');assert.equal((await validateNativeEvidence(e,NOW)).p_kind,'NATIVE_ORDER');});
test('paired exit requires both distinct order identities and four independent producer receipts',async()=>{assert.equal((await validateNativeEvidence(await evidence(pair(),'PAIRED_TERMINAL'),NOW)).p_kind,'PAIRED_TERMINAL');});
for(const [name,change] of [
  ['bool quantity',f=>f.filled_quantity=true],['unknown state',f=>f.order_status='UNKNOWN'],['missing native mapping hash',f=>delete f.order_binding_sha256],
  ['unknown account position',f=>f.position_quantity=null],['native cannot self-report MATCHED',f=>f.reconciliation={status:'MATCHED'}],
  ['terminal pending orders',f=>f.pending_order_count=1],['two lots',f=>f.position_quantity=2]]){
  test(name+' cannot reach database',async()=>{const f=facts();change(f);const e=await evidence(f);let calls=0;const r=await handleRequest(await signed(e,'broker_reader'),deps(async()=>{calls++;return null;}));assert.equal(r.status,400);assert.equal(calls,0);});
}
for(const [name,change] of [['cash drift',f=>f.reconciliation.broker.cash_cents=1],['cloned producer',f=>f.reconciliation.broker.producer_id='PRODUCER-ledger'],['wrong parent order',f=>f.reconciliation.broker.parent_order_id='UNRELATED'],['missing one party',f=>delete f.reconciliation.ledger]]){
  test('paired '+name+' is denied',async()=>{const f=pair();change(f);await assert.rejects(validateNativeEvidence(await evidence(f,'PAIRED_TERMINAL'),NOW));});
}
test('runtime HMAC cannot inject native reader facts',async()=>{const e=await evidence();e.source_sha256=S;let calls=0;const r=await handleRequest(await signed(e),deps(async()=>{calls++;}));assert.equal(r.status,400);assert.equal(calls,0);});
test('linked claim default-disabled independently of source implementation',async()=>{let calls=0;const r=await handleRequest(await signed(claim),deps(async()=>{calls++;},{claimEnabled:false}));assert.equal(r.status,503);assert.equal(calls,0);});
test('fresh linked close needs exact account reread and matching parent',async()=>{const r=await handleRequest(await signed(claim),deps(async(name)=>name==='gold2_paper_claim_linked_exit_v3'?state():state({claimed:false,status:'ACCOUNT_READ',claim_id:'CLOSE-CLM'})));assert.equal(r.status,200);assert.equal((await r.json()).claimed,true);});
for(const patch of [{position_origin_claim_id:'WRONG-PARENT'},{position_quantity:0,position_origin_claim_id:null},{freeze_reason:null}]){
 test('linked malformed relation revokes authority '+JSON.stringify(patch),()=>assert.throws(()=>validateCoordinatorReply(state(patch),claim,B)));
}
test('committed linked claim with lost ack never retries inside Edge',async()=>{let calls=0;const r=await handleRequest(await signed(claim),deps(async()=>{calls++;throw new Error('lost ack');}));assert.equal(r.status,503);assert.equal(calls,1);});
test('paired completion cannot return open position or release the freeze',()=>{const input={...C,op:'complete_linked_pair_v3',claim_id:'CLOSE-CLM'};const good=state({claimed:false,status:'PAIR_RECORDED',phase:'FROZEN',position_quantity:0,position_origin_claim_id:null,pending_claim_id:null,freeze_reason:'LINKED_EXIT_PAIR_RECONCILED_REVIEW_REQUIRED'});assert.equal(validateCoordinatorReply(good,input,B).phase,'FROZEN');for(const patch of [{phase:'FLAT',freeze_reason:null},{position_quantity:1,position_origin_claim_id:'OPEN-CLM'},{pending_claim_id:'CLOSE-CLM'}]) assert.throws(()=>validateCoordinatorReply({...good,...patch},input,B));});
test('native write uses independently reread immutable hash rather than returned label',async()=>{const e=await evidence();let calls=0;const stored={environment:e.environment,account_id:e.account_id,robot_id:e.robot_id,source_sha256:R,evidence_id:e.evidence_id,kind:e.kind,observed_at:e.observed_at,received_at:e.observed_at,facts:e.facts,facts_sha256:e.facts_sha256};const r=await handleRequest(await signed(e,'broker_reader'),deps(async name=>{calls++;return name==='gold2_paper_read_native_evidence_v3'?stored:{status:'MATCHED'};}));assert.equal(r.status,200);assert.equal(calls,2);assert.equal((await r.json()).status,'EVIDENCE_RECORDED');});
