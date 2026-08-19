#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DOCS=ROOT/'docs'/'os-vnext'; ARCH=ROOT/'docs'/'architecture'; SD=ROOT/'packages'/'contracts'/'schemas'/'vnext'
DOCS_REQ=['README.md','CONSTITUTION.md','RESEARCH-DEPENDENCY-GRAPH.md','AUTHORITY-PRECEDENCE.md','LEARNING-LOOP.md','SEVEN-QUESTIONS.md']
SCHEMA_REQ=['research-target.schema.json','canonical-observation.schema.json','evidence-claim.schema.json','research-state-vector.schema.json','capability-invocation.schema.json','capability-input-bundle.schema.json','capability-result.schema.json','execution-receipt.schema.json','future-settlement.schema.json','capability-revision.schema.json']
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def main():
 for n in DOCS_REQ: assert (DOCS/n).exists(), n
 for n in SCHEMA_REQ:
  o=load(SD/n); assert o['$schema']=='https://json-schema.org/draft/2020-12/schema' and o['type']=='object' and o['additionalProperties'] is False
 c=(DOCS/'CONSTITUTION.md').read_text(); d=(DOCS/'RESEARCH-DEPENDENCY-GRAPH.md').read_text(); l=(DOCS/'LEARNING-LOOP.md').read_text()
 for t in ['Lifetime Right-Tail Capture under Survival Constraints','X := (Xs, Xa, Xp)','Claim Authority <= Evidence Authority','ResearchCapability','Force score']: assert t in c
 assert 'not a claim that market reality always follows a one-way causal law' in d; assert 'Receipt = Ledger; Status = Projection' in l
 s=load(ARCH/'r2_2'/'R2-2-STATE.json'); assert s['status']=='candidate_started' and s['canonical_state_candidate']=='ResearchStateVector' and s['dependency_graph_is_universal_causal_law'] is False and s['migration_boundary']['existing_gold_ids_mutated'] is False
 r2=load(ARCH/'r2'/'R2-STATE.json'); assert r2['capability_count']==12 and r2['registry_entry_count']==99 and r2['canon_entry_count']==0
 canon=load(ARCH/'CANON-STATUS.json'); assert canon['projection_semantics']=='deterministic_non_authoritative_projection' and canon['stages']['R2_1']['status']=='accepted_merged' and canon['stages']['R3A']['status']=='paused_not_started'
 rs=load(SD/'research-state-vector.schema.json')['properties']; assert all(k in rs for k in ['P','Xs','N','V','Xa','Xp','S']) and rs['scalar_pnx_score_prohibited']['const'] is True and rs['force_classification_is_projection']['const'] is True
 assert load(SD/'execution-receipt.schema.json')['properties']['live_execution_authorized']['const'] is False
 print('R2.2 Research Intelligence Canon Re-foundation validation: PASS')
if __name__=='__main__': main()
