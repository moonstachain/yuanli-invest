#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ARCH=ROOT/'docs'/'architecture'
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def main():
 r1=load(ARCH/'r1'/'R1-STATE.json'); r2=load(ARCH/'r2'/'R2-STATE.json'); s=load(ARCH/'r2_1'/'R2-1-STATE.json'); m=load(ARCH/'r2_1'/'R2-1-MERGE-RECEIPT-v0.1.json')
 assert r1['status']=='accepted_merged'; assert r2['status']=='accepted_merged' and r2['canon_entry_count']==0
 assert s['status']=='accepted_merged' and s['merge_commit']=='19c2088231edde3bf5f8a4c70051c2f6506625db'
 assert m['pr_number']==20 and m['post_acceptance_ci']['run_number']==89 and m['post_acceptance_ci']['conclusion']=='success'
 assert m['merge_commit_sha']=='19c2088231edde3bf5f8a4c70051c2f6506625db'; assert s['live_execution']=='unavailable_by_design'
 print('R2.1 completed-state validation: PASS')
if __name__=='__main__': main()
