// Synthetic Ed25519/HMAC protocol fixtures only; no deployed keys or accounts.
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {canonical,objectHash,sha256} from '../supabase/functions/gold2-paper-control/core.mjs';
import {prepareAdmission,handleAdmission} from '../supabase/functions/gold2-paper-control/admission-v4.mjs';
import {handleRequest} from '../supabase/functions/gold2-paper-control/service.mjs';

import {BINDING,KEYS,NOW,identity,bootstrap,engineering,controlKeys,signed,serviceDeps} from './gold2_admission_v4_fixtures.mjs';

test('R2 preparation is engineering-only and roles cannot swap',async()=>{
 const input=await engineering();
 const [name,args]=await prepareAdmission(input,'runtime',BINDING,NOW);
 assert.equal(name,'gold2_paper_prepare_engineering_case');assert.equal(args.p_body.quantity,1);
 await assert.rejects(()=>prepareAdmission(input,'broker_reader',BINDING,NOW),{code:'ADMISSION_SCOPE_DENIED'});
 await assert.rejects(()=>prepareAdmission(bootstrap(),'runtime',BINDING,NOW),{code:'ADMISSION_SCOPE_DENIED'});
 for(const changes of [{reason:'ENTRY'},{quantity:2},{live_execution_authorized:true},{limit_price:'1000.12'},
  {stop_price:'995.99'},{credit_multiplier:'2'},{exit_not_after_at:new Date(NOW+120000).toISOString()}]){
  await assert.rejects(()=>engineering(changes).then(p=>prepareAdmission(p,'runtime',BINDING,NOW)));
 }
});
test('reader cannot provision policy, claim an order, or use runtime authentication',async()=>{
 let calls=0;const deps=serviceDeps(async()=>{calls++;},await controlKeys());
 for(const op of ['provision_reader_deployment','activate_engineering_policy','claim_order_v2']){
  const res=await handleRequest(await signed({op,...identity(true)},'broker_reader'),deps);
  assert.equal(res.status,400);
 }
 const res=await handleRequest(await signed(bootstrap(),'broker_reader',NOW,KEYS.runtime),deps);
 assert.equal(res.status,401);assert.equal(calls,0);
});
test('bootstrap acknowledgement is independently read and signing uses post-RPC clock',async()=>{
 let clock=NOW;const input=bootstrap(),scopeHash=await objectHash(input.scope),control=await controlKeys(),names=[];
 const common={...identity(true),deployment_id:'DIAGNOSTIC-DEPLOYMENT',scope_sha256:scopeHash,observed_at:new Date(NOW+5).toISOString()};
 const rpc=async name=>{names.push(name);clock+=10;return {...common,
  source:name.includes('admit_')?'independent_reader_journal_bootstrap_admission_v3':'independent_reader_bootstrap_readback_v4',
  status:name.includes('admit_')?'FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED':'BOOTSTRAP_READ_ONLY'};};
 const res=await handleRequest(await signed(input,'broker_reader'),serviceDeps(rpc,control,()=>clock));
 assert.equal(res.status,200);const receipt=await res.json();assert.ok(receipt.signature.startsWith('ed25519:'));
 assert.deepEqual(names,['gold2_paper_admit_reader_bootstrap','gold2_paper_read_reader_bootstrap']);
 const publicKey=await crypto.subtle.importKey('raw',Buffer.from(control.publicKeyBase64,'base64'),{name:'Ed25519'},false,['verify']);
 const material=Object.fromEntries(Object.entries(receipt).filter(([k])=>k!=='signature'));
 assert.ok(await crypto.subtle.verify('Ed25519',publicKey,Buffer.from(receipt.signature.slice(8),'hex'),new TextEncoder().encode(canonical(material))));
});
test('lost acknowledgement is UNKNOWN and a separate read does not resubmit',async()=>{
 const input=bootstrap(),control=await controlKeys();let writes=0;
 const stored={...identity(true),source:'independent_reader_bootstrap_readback_v4',status:'BOOTSTRAP_READ_ONLY',
  deployment_id:'DIAGNOSTIC-DEPLOYMENT',scope_sha256:await objectHash(input.scope),observed_at:new Date(NOW).toISOString()};
 const rpc=async name=>{if(name.includes('admit_')){writes++;throw new Error('fixture committed then ACK lost');}return stored;};
 const deps=serviceDeps(rpc,control);
 const first=await handleRequest(await signed(input,'broker_reader'),deps);
 assert.equal(first.status,503);assert.equal((await first.json()).status,'UNKNOWN_NO_RETRY');
 const read=await handleRequest(await signed({op:'read_reader_bootstrap',...identity(true)},'broker_reader'),deps);
 assert.equal(read.status,200);const receipt=await read.json();assert.equal(receipt.status,'BOOTSTRAP_READ_ONLY');
 assert.equal(receipt.observed_at,stored.observed_at);assert.equal(writes,1);
});
test('mismatched readback and control keypair fail closed',async()=>{
 const input=bootstrap(),control=await controlKeys();
 const stored={...identity(true),source:'independent_reader_journal_bootstrap_admission_v3',status:'FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED',
  deployment_id:'DIAGNOSTIC-DEPLOYMENT',scope_sha256:await objectHash(input.scope),observed_at:new Date(NOW).toISOString()};
 await assert.rejects(()=>handleAdmission(input,'broker_reader',{binding:BINDING,controlSigning:control,now:()=>NOW,
  rpc:async name=>name.includes('admit_')?stored:{...stored,scope_sha256:'sha256:'+'0'.repeat(64)}}),{code:'ADMISSION_WRITE_READBACK_UNKNOWN'});
 const other=await controlKeys();
 await assert.rejects(()=>handleAdmission({op:'read_reader_bootstrap',...identity(true)},'broker_reader',{
  binding:BINDING,controlSigning:{...control,publicKeyBase64:other.publicKeyBase64},now:()=>NOW,
  rpc:async()=>({...stored,source:'independent_reader_bootstrap_readback_v4',status:'BOOTSTRAP_READ_ONLY'})}),{code:'CONTROL_KEY_PAIR_MISMATCH'});
});
test('write acknowledgement cannot accept wrong readback identity or type',async()=>{
 const input=bootstrap(),control=await controlKeys();
 const stored={...identity(true),source:'independent_reader_journal_bootstrap_admission_v3',status:'FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED',
  deployment_id:'DIAGNOSTIC-DEPLOYMENT',scope_sha256:await objectHash(input.scope),observed_at:new Date(NOW).toISOString()};
 const read={...stored,source:'independent_reader_bootstrap_readback_v4',status:'BOOTSTRAP_READ_ONLY'};
 for(const changes of [{account_id:'WRONG'},{environment:'WRONG'},{robot_id:9},{source_sha256:'sha256:'+'f'.repeat(64)},
  {source:'WRONG'},{status:'WRONG'}]){
  await assert.rejects(()=>handleAdmission(input,'broker_reader',{binding:BINDING,controlSigning:control,now:()=>NOW,
   rpc:async name=>name.includes('admit_')?stored:{...read,...changes}}));
 }
});
