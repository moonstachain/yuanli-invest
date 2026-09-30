// Actual local PG17 admission review; all identities and sessions are synthetic.
// Replays candidate SQL into a disposable database and never contacts a broker.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import pg from '../../yuanli-invest-runtime-upgrade-20260925/node_modules/pg/lib/index.js';
import {canonical,objectHash} from '../supabase/functions/gold2-paper-control/core.mjs';
import {handleAdmission,signControlReceipt} from '../supabase/functions/gold2-paper-control/admission-v4.mjs';
import {handleRequest} from '../supabase/functions/gold2-paper-control/service.mjs';
import {BINDING,identity,bootstrap,engineering,controlKeys,signed,serviceDeps} from './gold2_admission_v4_fixtures.mjs';

const PYTHON=process.env.GOLD2_TEST_PYTHON||'python3';
const DB='gold2_paper_v4_review_'+process.pid;
const BASE='postgres://smoke:local-test-only@127.0.0.1:50440/';
const OUTPUT=path.resolve('../outputs/invest-os-closure-20260927/paper-review');
const migrations=['20260925072235_gold2_paper_private_receipts.sql','20260926081247_gold2_account_coordinator_v2.sql',
 '20260926113459_gold2_linked_protective_exit_v3.sql','20260927072225_gold2_engineering_and_reader_bootstrap_v4.sql'];
const checks=[],receipts=[],hashes=[];
const admin=new pg.Client({connectionString:BASE+'postgres'});let owner,service,removed=false;
const check=(name,condition=true)=>{assert.ok(condition,name);checks.push(name);};
const denied=async(name,fn,message)=>{await assert.rejects(fn,error=>error.message===message);check(name);};
const common=b=>({p_environment:b.environment,p_account_id:b.accountId,p_robot_id:b.robotId,p_source_sha256:b.readerSourceSha256});
const serviceClient=async()=>{const c=new pg.Client({connectionString:BASE+DB});await c.connect();await c.query('set role service_role');return c;};
async function rpcOn(c,name,args){
 assert.match(name,/^gold2_paper_[a-z0-9_]+$/);const keys=Object.keys(args);
 const text=`select public.${name}(${keys.map((k,i)=>`${k}=>$${i+1}`).join(',')}) as result`;
 const vals=keys.map(k=>args[k]!==null&&typeof args[k]==='object'?JSON.stringify(args[k]):args[k]);
 return (await c.query(text,vals)).rows[0].result;
}
const rpc=(name,args)=>rpcOn(service,name,args);
async function seed(account=BINDING.accountId){
 const b={...BINDING,accountId:account};
 await owner.query('insert into gold2_paper.runtime_bindings values($1,$2,$3,$4,$5,true)',
  [b.environment,account,b.robotId,b.sourceSha256,b.readerSourceSha256]);
 await owner.query('insert into gold2_paper.account_execution_state(environment,account_id) values($1,$2)',[b.environment,account]);
 await owner.query(`insert into gold2_paper.reader_deployments_v4 values($1,$2,$3,$4,$5,'PID-999999',$6,$7,true,clock_timestamp()+interval '1 hour')`,
  [b.environment,account,b.robotId,'DIAGNOSTIC-DEPLOYMENT-'+account,b.readerSourceSha256,'sha256:'+'c'.repeat(64),'sha256:'+'d'.repeat(64)]);
 return b;
}
function inputFor(b,nonce='1'.repeat(64)){
 const input=bootstrap(nonce);input.account_id=b.accountId;input.scope.account_id=b.accountId;return input;
}
async function admitArgs(input){return {...common({...BINDING,accountId:input.account_id}),p_scope:input.scope,
 p_scope_canonical:canonical(input.scope),p_scope_sha256:await objectHash(input.scope)};}
async function prepFixture(changes={},fee='80',budget='12500',margin='200000'){
 const item=await engineering(changes,Date.now());const body=item.body;
 const material=Object.fromEntries(Object.entries(body).filter(([k])=>k!=='contract_hash'));
 await owner.query(`insert into gold2_paper.engineering_policies_v4 values($1,$2,$3,'DIAGNOSTIC-CASE',$4,$5,$6,$7,$8,$9,$10,$11,$12,
 clock_timestamp()-interval '1 minute',clock_timestamp()+interval '1 hour',true,clock_timestamp()+interval '1 hour')
 on conflict(environment,account_id) do update set contract_hash=excluded.contract_hash,round_trip_fee_upper_cny=excluded.round_trip_fee_upper_cny,
 strategy_budget_cny=excluded.strategy_budget_cny,margin_one_lot_cny=excluded.margin_one_lot_cny`,
 [BINDING.environment,BINDING.accountId,BINDING.robotId,body.command_id,body.contract_hash,body.contract,fee,margin,budget,
 'sha256:'+'d'.repeat(64),body.human_approval_ref,body.program_approval_ref]);
 return {input:item,args:{p_environment:BINDING.environment,p_account_id:BINDING.accountId,p_robot_id:BINDING.robotId,
  p_source_sha256:BINDING.sourceSha256,p_body:body,p_body_canonical:canonical(material),p_broker_evidence_id:item.broker_evidence_id}};
}
async function evidenceAndAllocation(){
 const raw={raw_account_sha256:'sha256:'+'6'.repeat(64),raw_orders_sha256:'sha256:'+'6'.repeat(64),
  raw_trades_sha256:'sha256:'+'6'.repeat(64),raw_positions_sha256:'sha256:'+'6'.repeat(64)};
 const party={cash_cents:500000000,available_cents:490000000,frozen_margin_cents:10000000,position_quantity:0,filled_quantity:0};
 const facts={command_id:'DIAGNOSTIC-ENGINEERING-OPEN',claim_id:null,instrument:'au2612',action:'OPEN_LONG',order_id:null,
  order_status:'NONE',filled_quantity:0,position_quantity:0,pending_order_count:0,
  reconciliation:{broker:party,execution:party,ledger:party,expected:party},...raw};
 await rpc('gold2_paper_ingest_broker_evidence_v2',{...common(BINDING),p_evidence_id:'DIAGNOSTIC-PRECLAIM',p_kind:'PRE_CLAIM',
  p_observed_at:new Date(Date.now()-1).toISOString(),p_raw_sha256:await objectHash(raw),p_facts_sha256:await objectHash(facts),
  p_facts:facts,p_facts_canonical:canonical(facts),p_raw_canonical:canonical(raw)});
 const event={sequence:1,kind:'StrategyAllocationInitialized',command_id:'DIAGNOSTIC-ALLOCATION',at:new Date(Date.now()-1).toISOString(),
  data:{approval_ref:'DIAGNOSTIC-HUMAN',strategy_equity_cny:'5000000'},previous_hash:'0'.repeat(64)};
 event.event_hash=await objectHash(event);
 await rpc('gold2_paper_append_ledger_v1',{p_account_id:BINDING.accountId,p_robot_id:BINDING.robotId,p_events:[event],p_root_hash:event.event_hash});
}
try{
 await fs.mkdir(OUTPUT,{recursive:true,mode:0o700});await admin.connect();
 assert.equal((await admin.query('select count(*)::int n from pg_database where datname=$1',[DB])).rows[0].n,0,'refuse reuse unrelated test DB');
 await admin.query(`create database ${DB}`);owner=new pg.Client({connectionString:BASE+DB});await owner.connect();
 const version=(await owner.query('show server_version')).rows[0].server_version;assert.match(version,/^17\./);
 for(const file of migrations){const bytes=await fs.readFile(path.join('supabase/migrations',file));
  hashes.push({file,sha256:createHash('sha256').update(bytes).digest('hex')});await owner.query(bytes.toString());}
 const tables=['runtime_bindings','reader_deployments_v4','reader_bootstraps_v4','engineering_policies_v4','engineering_cases_v4'];
 const initial={};for(const table of tables) initial[table]=(await owner.query(`select count(*)::int n from gold2_paper.${table}`)).rows[0].n;
 check('migration provisions zero bindings/deployments/policies/admissions',Object.values(initial).every(n=>n===0));
 service=await serviceClient();
 await denied('service cannot provision reader deployment',()=>service.query('insert into gold2_paper.reader_deployments_v4(environment) values($1)',[BINDING.environment]),'permission denied for table reader_deployments_v4');
 await denied('service cannot change engineering policy',()=>service.query('update gold2_paper.engineering_policies_v4 set active=true'),'permission denied for table engineering_policies_v4');
 const privilege=(await owner.query(`select not has_table_privilege('anon','gold2_paper.engineering_cases_v4','SELECT')
 and not has_function_privilege('authenticated','public.gold2_paper_admit_reader_bootstrap(text,text,bigint,text,jsonb,text,text)','EXECUTE') ok`)).rows[0].ok;
 check('anon/authenticated cannot read or admit',privilege);
 await seed();const keys=await controlKeys(),input=bootstrap();const deps=serviceDeps(rpc,keys,Date.now);
 const response=await handleRequest(await signed(input,'broker_reader',Date.now()),deps);assert.equal(response.status,200);
 const receipt=await response.json();receipts.push(receipt);check('actual Edge HMAC -> service SQL -> independent read -> Ed25519 bootstrap');
 const python=spawnSync(PYTHON,
  ['-c','import json,sys,base64; from yuanli_invest.gold_au_control_admission import PinnedControlVerifier; x=json.load(sys.stdin); print(json.dumps(PinnedControlVerifier(base64.b64decode(x["public"]))(x["receipt"])))'],
  {cwd:process.cwd(),env:{...process.env,PYTHONPATH:'src'},input:JSON.stringify({public:keys.publicKeyBase64,receipt}),encoding:'utf8'});
 assert.equal(python.status,0,python.stderr);check('actual Python3.12 pinned verifier accepts Edge signed receipt',JSON.parse(python.stdout).status==='SIGNATURE_VERIFIED_WITH_PINNED_KEY');
 const retry=await rpc('gold2_paper_admit_reader_bootstrap',await admitArgs(input));
 check('exact retry preserves original admission timestamp',retry.observed_at===receipt.observed_at);
 const rotatedKey='fixture-rotated-reader-key-not-production-32chars';
 const rotated=await handleRequest(await signed(bootstrap('2'.repeat(64)),'broker_reader',Date.now(),rotatedKey),{...deps,readerKey:rotatedKey});
 check('new reader HMAC key cannot renew stable account',rotated.status===503&&(await rotated.json()).status==='UNKNOWN_NO_RETRY');
 await denied('different nonce cannot renew stable account',async()=>rpc('gold2_paper_admit_reader_bootstrap',await admitArgs(bootstrap('2'.repeat(64)))),'GOLD2_BOOTSTRAP_ALREADY_CONSUMED');
 for(const [name,field,value] of [['PID','reader_process_id','PID-123456'],['journal path','journal_path_sha256','sha256:'+'f'.repeat(64)]]){
  await owner.query(`update gold2_paper.reader_deployments_v4 set ${field}=$1`,[value]);const changed=structuredClone(input);changed.scope[field]=value;
  await denied('changed '+name+' cannot renew stable account',async()=>rpc('gold2_paper_admit_reader_bootstrap',await admitArgs(changed)),'GOLD2_BOOTSTRAP_ALREADY_CONSUMED');
  await owner.query(`update gold2_paper.reader_deployments_v4 set ${field}=$1`,[input.scope[field]]);
 }
 const source='sha256:'+'9'.repeat(64);await owner.query('update gold2_paper.runtime_bindings set reader_source_sha256=$1',[source]);
 await owner.query('update gold2_paper.reader_deployments_v4 set reader_source_sha256=$1',[source]);
 const changed=structuredClone(input);changed.source_sha256=source;changed.scope.reader_source_sha256=source;
 const changedArgs=await admitArgs(changed);changedArgs.p_source_sha256=source;
 await denied('admin rotated source cannot renew stable account',()=>rpc('gold2_paper_admit_reader_bootstrap',changedArgs),'GOLD2_BOOTSTRAP_ALREADY_CONSUMED');
 await owner.query('update gold2_paper.runtime_bindings set reader_source_sha256=$1',[BINDING.readerSourceSha256]);
 await owner.query("update gold2_paper.reader_deployments_v4 set reader_source_sha256=$1,reader_process_id='PID-999999',journal_path_sha256=$2",[BINDING.readerSourceSha256,'sha256:'+'c'.repeat(64)]);
 const lossB=await seed('DIAGNOSTIC-LOSS-ACK');const lossInput=inputFor(lossB);let writes=0;
 const lossRpc=async(name,args)=>{const result=await rpc(name,args);if(name.includes('admit_')){writes++;throw new Error('synthetic lost response after autocommitted SQL');}return result;};
 const lossDeps={...serviceDeps(lossRpc,keys,Date.now),binding:lossB};
 const lost=await handleRequest(await signed(lossInput,'broker_reader',Date.now()),lossDeps);
 check('committed SQL with lost ACK returns UNKNOWN_NO_RETRY',lost.status===503&&(await lost.json()).status==='UNKNOWN_NO_RETRY');
 const readInput={op:'read_reader_bootstrap',environment:lossB.environment,account_id:lossB.accountId,robot_id:lossB.robotId,source_sha256:lossB.readerSourceSha256};
 const read=await handleRequest(await signed(readInput,'broker_reader',Date.now()),lossDeps);
 check('separate read recovers lost ACK without second write',read.status===200&&writes===1);
 check('lost ACK persisted exactly one bootstrap',(await owner.query('select count(*)::int n from gold2_paper.reader_bootstraps_v4 where account_id=$1',[lossB.accountId])).rows[0].n===1);
 const cb=await seed('DIAGNOSTIC-CONCURRENT');const clients=await Promise.all(Array.from({length:12},()=>serviceClient()));
 const race=await Promise.allSettled(clients.map(async(c,i)=>rpcOn(c,'gold2_paper_admit_reader_bootstrap',await admitArgs(inputFor(cb,(i+3).toString(16).padStart(64,'0'))))));
 await Promise.all(clients.map(c=>c.end()));
 check('12 concurrent distinct attempts admit exactly one',race.filter(r=>r.status==='fulfilled').length===1&&race.filter(r=>r.status==='rejected'&&r.reason.message==='GOLD2_BOOTSTRAP_ALREADY_CONSUMED').length===11);
 await denied('bootstrap history is immutable',()=>owner.query("update gold2_paper.reader_bootstraps_v4 set deployment_id='CHANGED'"),'GOLD2_HISTORY_APPEND_ONLY');
 const unqualified=await prepFixture();
 await denied('engineering cannot prepare without independent broker evidence',()=>rpc('gold2_paper_prepare_engineering_case',unqualified.args),'GOLD2_BOUND_BROKER_EVIDENCE_REQUIRED');
 await evidenceAndAllocation();
 // Today may be Sunday. These SQL fixtures use a synthetic provisioned window;
 // they do not establish an official live session. Edge coarse gate is separately tested.
 for(const [name,changes,fee,budget,margin] of [
  ['round trip fees exceed R2',{},'800.00001','12500','200000'],
  ['reduced strategy budget below R2',{},'80','4279.99','200000'],
  ['stop farther than four yuan',{stop_price:'995.99'},'0','12500','200000'],
  ['deadline longer than 120 seconds',{exit_not_after_at:new Date(Date.now()+121000).toISOString()},'80','12500','200000'],
  ['deadline before decision',{exit_not_after_at:new Date(Date.now()-2000).toISOString()},'80','12500','200000'],
  ['quote/reference exceeds 0.1',{reference_price:'999.91'},'80','12500','200000'],
  ['excess one lot margin',{},'80','12500','1500000.01']]){
  const f=await prepFixture(changes,fee,budget,margin);await denied(name,()=>rpc('gold2_paper_prepare_engineering_case',f.args),name==='excess one lot margin'?'GOLD2_ENGINEERING_BROKER_NOT_FLAT_OR_MARGIN':'GOLD2_ENGINEERING_R2_LIMIT_DENIED');
 }
 const valid=await prepFixture({},'800','5000');const prepared=await rpc('gold2_paper_prepare_engineering_case',valid.args);receipts.push(prepared);
 check('exact fee-inclusive R2 boundary 5000 accepted',prepared.status==='ENGINEERING_PREPARED'&&prepared.counts_as_strategy_return_sample===false&&prepared.starts_formal_30_day_clock===false&&prepared.exit_on_first_verified_fill===true);
 check('prepared exact retry original timestamp',(await rpc('gold2_paper_prepare_engineering_case',valid.args)).observed_at===prepared.observed_at);
 const observed=await rpc('gold2_paper_read_engineering_case',{p_environment:BINDING.environment,p_account_id:BINDING.accountId,p_robot_id:BINDING.robotId,p_source_sha256:BINDING.sourceSha256});
 check('engineering readback preserves original evidence/time',observed.status==='ENGINEERING_READ_ONLY'&&observed.observed_at===prepared.observed_at&&observed.broker_evidence_id===prepared.broker_evidence_id);
 const signedPrepared=await signControlReceipt(prepared,keys,Date.now());
 const verifyPrepared=spawnSync(PYTHON,
  ['-c','import json,sys,base64; from datetime import datetime,timezone; from scripts.gold_au_engineering_bootstrap import verified_preparation; from yuanli_invest.gold_au_control_admission import PinnedControlVerifier; x=json.load(sys.stdin); r=verified_preparation(x["receipt"],PinnedControlVerifier(base64.b64decode(x["public"])),x["body"],datetime.now(timezone.utc)); print(r["status"])'],
  {cwd:process.cwd(),env:{...process.env,PYTHONPATH:'src'},input:JSON.stringify({public:keys.publicKeyBase64,receipt:signedPrepared,body:valid.input.body}),encoding:'utf8'});
 assert.equal(verifyPrepared.status,0,verifyPrepared.stderr);
 check('actual SQL preparation -> Ed25519 signer -> Python exact engineering verifier',verifyPrepared.stdout.trim()==='ENGINEERING_PREPARED');
 const manifest={status:'PASS',local_only:true,synthetic_fixtures:true,official_session_proven:false,broker_orders:0,version,checks,initial_counts:initial,migrations:hashes,receipts,
  cleanup:'disposable database dropped after committed synthetic concurrency/lost-ACK fixtures'};
 await fs.writeFile(path.join(OUTPUT,'pg17-admission-review.json'),JSON.stringify(manifest,null,2)+'\n',{mode:0o600});
 console.log(JSON.stringify({status:'PASS',checks:checks.length,version,evidence:path.join(OUTPUT,'pg17-admission-review.json')}));
}finally{
 await service?.end();await owner?.end();
 if(admin._connected){const existing=(await admin.query('select 1 from pg_database where datname=$1',[DB])).rowCount;
  if(existing){await admin.query(`drop database ${DB}`);removed=(await admin.query('select count(*)::int n from pg_database where datname=$1',[DB])).rows[0].n===0;
   const resultPath=path.join(OUTPUT,'pg17-admission-review.json');
   try{const m=JSON.parse(await fs.readFile(resultPath,'utf8'));m.disposable_database_removed_verified=removed;await fs.writeFile(resultPath,JSON.stringify(m,null,2)+'\n',{mode:0o600});}catch{}}await admin.end();}
 if(removed)console.log('DISPOSABLE_DATABASE_REMOVED');
}
