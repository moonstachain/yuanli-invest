from scripts.validate_yqs0_supabase_kernel import (
    validate_architecture_text,
    validate_inventory,
    validate_pit_law,
    validate_rls,
    validate_stage_state,
    validate_worker_contract,
)


def test_yqs0_inventory_contract():
    validate_inventory()


def test_yqs0_pit_law():
    validate_pit_law()


def test_yqs0_rls_authority_matrix():
    validate_rls()


def test_yqs0_quant_worker_contract():
    validate_worker_contract()


def test_yqs0_stage_authority_boundaries():
    validate_stage_state()


def test_yqs0_architecture_text_invariants():
    validate_architecture_text()
