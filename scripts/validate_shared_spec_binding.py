from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def load(p): return yaml.safe_load((ROOT/p).read_text())
b=load("governance/shared-spec/yuanli-shared-spec-binding.v0.1.yaml")
p=load("governance/shared-spec/domain-profile.v0.1.yaml")
r=load("governance/receipts/shared-spec-binding-genesis-invest.v0.1.yaml")
assert b["project_id"]=="YIP"
assert b["registry_ref"]["version"]=="v0.2"
assert b["ready_state"]=="READY_WITH_LIMITS"
assert all(x["pin_policy"]=="PIN_EXACT_COMMIT_FOR_REGULATED_OR_HIGH_EFFECT_RUNTIME" for x in b["bindings"])
auth=next(x for x in b["bindings"] if x["spec_id"]=="HumanAuthorization")
provider=next(x for x in b["bindings"] if x["spec_id"]=="ProviderContract")
assert auth["canonical_state"]=="ACTIVE_SHARED_RULE"
assert provider["owner"]=="COM0"
assert p["mappings"]["HumanAuthorization"]["capital_action_requires_separate_authority"] is True
assert p["mappings"]["ProviderContract"]["provider_ne_semantic_authority"] is True
assert r["binding_effect"]["capital_action_authorized"] is False
print("YIP SHARED SPEC BINDING VALID")
