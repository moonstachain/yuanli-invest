// Narrow admission protocol. An admission is never an order or allocation.
import {Denied, canonical, objectHash, sha256} from './core.mjs';

export const ADMISSION_OPS = new Set(['prepare_engineering_case','read_engineering_case',
  'admit_reader_bootstrap','read_reader_bootstrap']);
const COMMON=['op','environment','account_id','robot_id','source_sha256'];
const SHA=/^sha256:[0-9a-f]{64}$/;
const ID=/^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$/;
const COMMAND=['schema_version','program','command_id','action_contract_id','execution_intent_id',
  'capital_admission_id','human_approval_ref','program_approval_ref','decision_at','issued_at','not_before_at',
  'expires_at','environment','account_id','robot_id','contract','action','reason','quantity','reference_price',
  'limit_price','stop_price','exit_not_after_at','roll_not_after_at','credit_multiplier','volatility_multiplier',
  'max_slippage_bps','evidence_hash','contract_hash','live_execution_authorized','real_capital_movement_authorized'];
function exact(v,keys){return v&&typeof v==='object'&&!Array.isArray(v)
 &&Object.keys(v).sort().join('\0')===[...keys].sort().join('\0');}
function decimal(v){if(typeof v!=='string'||!/^\d+(?:\.\d+)?$/.test(v))throw new Denied('ENGINEERING_DECIMAL_REQUIRED');return Number(v);}
function time(v){if(typeof v!=='string'||!/(?:Z|[+-]\d\d:\d\d)$/.test(v)||!Number.isFinite(Date.parse(v)))throw new Denied('ADMISSION_AWARE_TIME_REQUIRED');return Date.parse(v);}

export async function prepareAdmission(input,role,binding,now){
 const reader=input.op.endsWith('reader_bootstrap');
 if(role!==(reader?'broker_reader':'runtime')||input.source_sha256!==(reader?binding.readerSourceSha256:binding.sourceSha256))
  throw new Denied('ADMISSION_SCOPE_DENIED');
 const args={p_environment:input.environment,p_account_id:input.account_id,p_robot_id:input.robot_id,p_source_sha256:input.source_sha256};
 if(input.op.startsWith('read_')){
  if(!exact(input,COMMON))throw new Denied('ADMISSION_READ_SHAPE');
  return ['gold2_paper_'+input.op,args];
 }
 if(input.op==='admit_reader_bootstrap'){
  const s=input.scope;
  if(!exact(input,[...COMMON,'scope'])||!exact(s,['environment','account_id','robot_id','reader_source_sha256',
   'reader_process_id','journal_path_sha256','bootstrap_attempt_nonce'])
   ||s.environment!==input.environment||s.account_id!==input.account_id||s.robot_id!==input.robot_id
   ||s.reader_source_sha256!==input.source_sha256||!/^PID-[0-9]+$/.test(s.reader_process_id)
   ||!SHA.test(s.journal_path_sha256)||!/^[0-9a-f]{64}$/.test(s.bootstrap_attempt_nonce))throw new Denied('BOOTSTRAP_SCOPE_SHAPE');
  return ['gold2_paper_admit_reader_bootstrap',{...args,p_scope:s,p_scope_canonical:canonical(s),p_scope_sha256:await objectHash(s)}];
 }
 const b=input.body;
 if(input.op!=='prepare_engineering_case'||!exact(input,[...COMMON,'body','broker_evidence_id'])
  ||!exact(b,COMMAND)||!ID.test(input.broker_evidence_id)||b.schema_version!=='1.0.0'
  ||b.program!=='GOLD2_AU_V1_BROKER_PAPER'||b.environment!==input.environment||b.account_id!==input.account_id
  ||b.robot_id!==input.robot_id||b.action!=='OPEN_LONG'||b.reason!=='ENGINEERING_TEST'||b.quantity!==1
  ||b.live_execution_authorized!==false||b.real_capital_movement_authorized!==false
  ||!/^au\d{4}$/.test(b.contract)||!SHA.test(b.contract_hash)||!SHA.test(b.evidence_hash)
  ||['command_id','action_contract_id','execution_intent_id','capital_admission_id','human_approval_ref','program_approval_ref'].some(k=>!ID.test(b[k])))
   throw new Denied('ENGINEERING_CONTRACT_SHAPE');
 const stripped=Object.fromEntries(Object.entries(b).filter(([k])=>k!=='contract_hash'));
 if(await objectHash(stripped)!==b.contract_hash)throw new Denied('ENGINEERING_CONTRACT_HASH');
 const price=decimal(b.limit_price),stop=decimal(b.stop_price),ref=decimal(b.reference_price),slip=decimal(b.max_slippage_bps);
 const credit=decimal(b.credit_multiplier),vol=decimal(b.volatility_multiplier);
 const decision=time(b.decision_at),issued=time(b.issued_at),start=time(b.not_before_at),end=time(b.expires_at);
 const exit=time(b.exit_not_after_at),roll=time(b.roll_not_after_at);
 const local=new Date(now+8*3600000),hour=local.getUTCHours(),minute=local.getUTCMinutes();
 const minuteOfDay=hour*60+minute;
 // The independently provisioned policy also binds an official session;
 // this coarse gate rejects nights/weekends and exchange recesses.
 const day=local.getUTCDay(),open=[ [540,615],[630,690],[810,900] ].some(([a,z])=>minuteOfDay>=a&&minuteOfDay<z);
 if(day===0||day===6||!open||!(decision<=issued&&issued<=start&&start<=now&&now<=end&&end<=exit)
  ||exit<=decision||exit-decision>120000||roll<=decision||roll>exit||price<=stop||price-stop>4
  ||price<=0||stop<=0||Math.abs(price-ref)>0.10000001||slip>20
  ||![0.5,1].includes(credit)||![0.5,1].includes(vol)
  ||Math.abs(price/0.02-Math.round(price/0.02))>1e-6||Math.abs(stop/0.02-Math.round(stop/0.02))>1e-6)
   throw new Denied('ENGINEERING_R2_OR_SESSION_DENIED');
 return ['gold2_paper_prepare_engineering_case',{...args,p_body:b,p_body_canonical:canonical(stripped),p_broker_evidence_id:input.broker_evidence_id}];
}

export async function signControlReceipt(result, {privateKeyBase64,publicKeyBase64}, now){
 const rawPublic=Uint8Array.from(atob(publicKeyBase64),c=>c.charCodeAt(0));
 const rawPrivate=Uint8Array.from(atob(privateKeyBase64),c=>c.charCodeAt(0));
 if(rawPublic.length!==32||rawPrivate.length<48)throw new Denied('CONTROL_SIGNING_DISABLED');
 if(!result||time(result.observed_at)>now)throw new Denied('CONTROL_RECEIPT_TIME_DENIED');
 const material={...result,signer_key_fingerprint:'sha256:'+await sha256(rawPublic)};
 const receipt={...material,raw_sha256:await objectHash(material)};
 const key=await crypto.subtle.importKey('pkcs8',rawPrivate,{name:'Ed25519'},false,['sign']);
 const bytes=new TextEncoder().encode(canonical(receipt));
 const signed=new Uint8Array(await crypto.subtle.sign('Ed25519',key,bytes));
 const publicKey=await crypto.subtle.importKey('raw',rawPublic,{name:'Ed25519'},false,['verify']);
 if(!await crypto.subtle.verify('Ed25519',publicKey,signed,bytes))throw new Denied('CONTROL_KEY_PAIR_MISMATCH');
 return {...receipt,signature:'ed25519:'+Array.from(signed,b=>b.toString(16).padStart(2,'0')).join('')};
}

export async function handleAdmission(input,role,{binding,rpc,controlSigning,now}){
 if(!controlSigning?.privateKeyBase64||!controlSigning?.publicKeyBase64)throw new Denied('CONTROL_SIGNING_DISABLED');
 const [name,args]=await prepareAdmission(input,role,binding,now());
 const result=await rpc(name,args);
 if(!result)return {httpStatus:404,payload:{status:'ADMISSION_NOT_FOUND'}};
 if(result.environment!==input.environment||result.account_id!==input.account_id||result.robot_id!==input.robot_id
  ||result.source_sha256!==input.source_sha256)throw new Denied('ADMISSION_REPLY_IDENTITY');
 const expected={prepare_engineering_case:['independent_gold2_engineering_preparation_v4','ENGINEERING_PREPARED'],
  read_engineering_case:['independent_gold2_engineering_readback_v4','ENGINEERING_READ_ONLY'],
  admit_reader_bootstrap:['independent_reader_journal_bootstrap_admission_v3','FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED'],
  read_reader_bootstrap:['independent_reader_bootstrap_readback_v4','BOOTSTRAP_READ_ONLY']}[input.op];
 if(result.source!==expected[0]||result.status!==expected[1])throw new Denied('ADMISSION_REPLY_SHAPE');
 if(input.op==='admit_reader_bootstrap'&&result.scope_sha256!==args.p_scope_sha256)throw new Denied('BOOTSTRAP_REPLY_SCOPE');
 if(input.op==='prepare_engineering_case'&&(result.command_id!==input.body.command_id||result.contract_hash!==input.body.contract_hash))
  throw new Denied('ENGINEERING_REPLY_CONTRACT');
 if(!input.op.startsWith('read_')){
  const read=await rpc('gold2_paper_read_'+(input.op==='admit_reader_bootstrap'?'reader_bootstrap':'engineering_case'),
   Object.fromEntries(Object.entries(args).filter(([k])=>['p_environment','p_account_id','p_robot_id','p_source_sha256'].includes(k))));
  const keys=input.op==='admit_reader_bootstrap'?['deployment_id','scope_sha256','observed_at']:['case_id','command_id','contract_hash','observed_at'];
  const readSource=input.op==='admit_reader_bootstrap'?'independent_reader_bootstrap_readback_v4':'independent_gold2_engineering_readback_v4';
  const readStatus=input.op==='admit_reader_bootstrap'?'BOOTSTRAP_READ_ONLY':'ENGINEERING_READ_ONLY';
  if(!read||keys.some(k=>read[k]!==result[k])
   ||['environment','account_id','robot_id','source_sha256'].some(k=>read[k]!==input[k])
   ||read.source!==readSource||read.status!==readStatus)throw new Denied('ADMISSION_WRITE_READBACK_UNKNOWN');
 }
 return {httpStatus:200,payload:await signControlReceipt(result,controlSigning,now())};
}
