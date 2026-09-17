import unittest

from scripts.yci0_rp1_g6_admit import (
    build_admission_decision,
    dedupe_by_content_hash,
)


def full_receipt():
    entities=[]
    for entity,cohort in (("MSFT","HYPERSCALER"),("NVDA","COMPUTE"),("ANET","NETWORKING"),("ETN","POWER_ELECTRICAL")):
        entities.append({
            "entity_id":entity,"cohort":cohort,"qualification":"QUALIFIED","blockers":[],
            "derived":{
                component:{"qualified":True,"latest_four_periods":["2025Q3","2025Q4","2026Q1","2026Q2"],"latest_four_values":["1","2","3","4"],"latest_four_receipts":[f"{entity}-{component}-{i}" for i in range(4)]}
                for component in ("INCREMENTAL_ROIC","CASH_CONVERSION","CAPITAL_INTENSITY")
            },
        })
    archives=[]
    for entity in ("MSFT","NVDA","ANET","ETN"):
        for kind in ("companyfacts","submissions"):
            archives.append({"entity_id":entity,"kind":kind,"sha256":f"{entity}-{kind}","storage_readback_sha256":f"{entity}-{kind}"})
    return {
        "status":"PASS","archive_mode":"PRIVATE_S3_SHA_READBACK","g6_coverage_status":"FULL",
        "qualified_entities":["MSFT","NVDA","ANET","ETN"],"entities":entities,"archives":archives,
        "authority":{"evidence_promotion_authorized":False,"research_authorized":False,"capital_authorized":False,"execution_authorized":False},
    }


def partial_receipt():
    r=full_receipt()
    r["g6_coverage_status"]="PARTIAL"
    r["qualified_entities"]=["MSFT"]
    for entity in r["entities"]:
        if entity["entity_id"]!="MSFT":
            entity["qualification"]="UNKNOWN"
            entity["blockers"]=["SEMANTIC_REGIME_BREAK"]
            entity["derived"]={}
    return r


class G6AdmissionTests(unittest.TestCase):
    def test_partial_coverage_produces_zero_mutation_plan_and_unknown_g6(self):
        d=build_admission_decision(partial_receipt())
        self.assertEqual(d["admission_status"],"BLOCKED_BY_COVERAGE")
        self.assertEqual(d["g6_state"],"UNKNOWN")
        self.assertEqual(d["mutation_plan"],[])
        self.assertEqual(d["qualified_metric_identities"],3)
        self.assertEqual(d["current_scope"],"PARTIAL_REALITY_STATE_5_OF_6")

    def test_missing_raw_readback_produces_zero_mutation(self):
        r=full_receipt(); r["archives"][0]["storage_readback_sha256"]="mismatch"
        d=build_admission_decision(r)
        self.assertEqual(d["admission_status"],"BLOCKED_BY_RAW_READBACK")
        self.assertEqual(d["mutation_plan"],[])

    def test_all_twelve_mandatory_metric_identities_are_required(self):
        r=full_receipt(); r["entities"][0]["derived"]["INCREMENTAL_ROIC"]["qualified"]=False
        d=build_admission_decision(r)
        self.assertEqual(d["admission_status"],"BLOCKED_BY_COVERAGE")
        self.assertEqual(d["qualified_metric_identities"],11)
        self.assertEqual(d["mutation_plan"],[])

    def test_full_coverage_builds_exactly_twelve_research_candidates_but_still_holds_transition(self):
        d=build_admission_decision(full_receipt())
        self.assertEqual(d["admission_status"],"READY_FOR_ADDITIVE_WRITE")
        self.assertEqual(len(d["mutation_plan"]),12)
        self.assertTrue(all(x["authority"]=="RESEARCH" for x in d["mutation_plan"]))
        self.assertEqual(d["transition_suggestion"],"HOLD")
        self.assertEqual(d["journey_stage"],"02 EVIDENCE")
        self.assertEqual(d["current_scope"],"PARTIAL_REALITY_STATE_5_OF_6")
        self.assertEqual(d["candidate_scope"],"FULL_REALITY_STATE_6_OF_6")
        self.assertEqual(d["physical_readback_required"],True)

    def test_duplicate_content_hash_is_idempotent(self):
        rows=[{"content_hash":"a","x":1},{"content_hash":"a","x":2},{"content_hash":"b","x":3}]
        out=dedupe_by_content_hash(rows)
        self.assertEqual([x["content_hash"] for x in out],["a","b"])
        self.assertEqual(out[0]["x"],1)

    def test_archive_authority_leakage_blocks_all_mutation(self):
        r=full_receipt(); r["authority"]["research_authorized"]=True
        d=build_admission_decision(r)
        self.assertEqual(d["admission_status"],"BLOCKED_BY_AUTHORITY_LEAKAGE")
        self.assertEqual(d["mutation_plan"],[])


if __name__ == "__main__":
    unittest.main()
