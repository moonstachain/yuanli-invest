// Ephemeral protocol fixtures only; never production identity or credentials.
import {sha256,objectHash} from '../supabase/functions/gold2-paper-control/core.mjs';
export const BINDING={environment:'SIMNOW_FIRST_NORMAL',accountId:'DIAGNOSTIC-ADMISSION-NOT-BROKER',robotId:2147482999,
 sourceSha256:'sha256:'+'a'.repeat(64),readerSourceSha256:'sha256:'+'b'.repeat(64)};
export const KEYS={signal:'fixture-signal-key-not-production-32chars',runtime:'fixture-runtime-key-not-production-32chars',broker_reader:'fixture-reader-key-not-production-32chars'};
export const NOW=Date.parse('2026-09-29T09:01:00+08:00');
export const identity=reader=>({environment:BINDING.environment,account_id:BINDING.accountId,robot_id:BINDING.robotId,
 source_sha256:reader?BINDING.readerSourceSha256:BINDING.sourceSha256});
export function bootstrap(nonce='1'.repeat(64)) {return {op:'admit_reader_bootstrap',...identity(true),scope:{
 environment:BINDING.environment,account_id:BINDING.accountId,robot_id:BINDING.robotId,
 reader_source_sha256:BINDING.readerSourceSha256,reader_process_id:'PID-999999',
 journal_path_sha256:'sha256:'+'c'.repeat(64),bootstrap_attempt_nonce:nonce}};}
export async function engineering(changes={},now=NOW){
 const body={schema_version:'1.0.0',program:'GOLD2_AU_V1_BROKER_PAPER',command_id:'DIAGNOSTIC-ENGINEERING-OPEN',
 action_contract_id:'DIAGNOSTIC-AC',execution_intent_id:'DIAGNOSTIC-EI',capital_admission_id:'DIAGNOSTIC-CA',
 human_approval_ref:'DIAGNOSTIC-HUMAN',program_approval_ref:'DIAGNOSTIC-PROGRAM',
 decision_at:new Date(now-1000).toISOString(),issued_at:new Date(now-500).toISOString(),
 not_before_at:new Date(now-500).toISOString(),expires_at:new Date(now+119000).toISOString(),
 environment:BINDING.environment,account_id:BINDING.accountId,robot_id:BINDING.robotId,
 contract:'au2612',action:'OPEN_LONG',reason:'ENGINEERING_TEST',quantity:1,reference_price:'1000.00',
 limit_price:'1000.02',stop_price:'996.02',exit_not_after_at:new Date(now+119000).toISOString(),
 roll_not_after_at:new Date(now+119000).toISOString(),credit_multiplier:'0.5',volatility_multiplier:'1',
 max_slippage_bps:'20',evidence_hash:'sha256:'+'e'.repeat(64),
 live_execution_authorized:false,real_capital_movement_authorized:false,...changes};
 body.contract_hash=await objectHash(body);
 return {op:'prepare_engineering_case',...identity(false),body,broker_evidence_id:'DIAGNOSTIC-PRECLAIM'};
}
export async function controlKeys(){
 const pair=await crypto.subtle.generateKey({name:'Ed25519'},true,['sign','verify']);
 return {privateKeyBase64:Buffer.from(await crypto.subtle.exportKey('pkcs8',pair.privateKey)).toString('base64'),
 publicKeyBase64:Buffer.from(await crypto.subtle.exportKey('raw',pair.publicKey)).toString('base64')};
}
export async function signed(input,role,now=NOW,key=KEYS[role]){
 const body=JSON.stringify(input),timestamp=new Date(now).toISOString();
 const material='GOLD2-PAPER-V1\nPOST\n/functions/v1/gold2-paper-control\n'+timestamp+'\n'+await sha256(body);
 const hmac=await crypto.subtle.importKey('raw',new TextEncoder().encode(key),{name:'HMAC',hash:'SHA-256'},false,['sign']);
 const signature=Buffer.from(await crypto.subtle.sign('HMAC',hmac,new TextEncoder().encode(material))).toString('hex');
 return new Request('https://example.invalid/functions/v1/gold2-paper-control',{method:'POST',body,headers:{
  'content-type':'application/json','x-gold2-role':role,'x-gold2-timestamp':timestamp,'x-gold2-signature':'sha256='+signature}});
}
export function serviceDeps(rpc,controlSigning,now=()=>NOW){return {enabled:true,claimEnabled:false,
 signalKey:KEYS.signal,runtimeKey:KEYS.runtime,readerKey:KEYS.broker_reader,binding:BINDING,rpc,controlSigning,now};}

