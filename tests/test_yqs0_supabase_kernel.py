import unittest

from scripts.validate_yqs0_supabase_kernel import (
    validate_architecture_text,
    validate_inventory,
    validate_pit_law,
    validate_rls,
    validate_stage_state,
    validate_worker_contract,
)


class YQS0SupabaseKernelTests(unittest.TestCase):
    def test_inventory_contract(self):
        validate_inventory()

    def test_pit_law(self):
        validate_pit_law()

    def test_rls_authority_matrix(self):
        validate_rls()

    def test_quant_worker_contract(self):
        validate_worker_contract()

    def test_stage_authority_boundaries(self):
        validate_stage_state()

    def test_architecture_text_invariants(self):
        validate_architecture_text()


if __name__ == "__main__":
    unittest.main()
