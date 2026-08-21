import copy
import unittest

from scripts import validate_me0_multi_engine_ontology as me0


class ME0OntologyTests(unittest.TestCase):
    def test_repository_me0_candidate_passes(self):
        me0.main()

    def test_closed_world_engine_registry_is_rejected(self):
        contract = me0.load_json(me0.CONTRACT_PATH)
        contract["governance"]["engine_registry_closed_world"] = True
        with self.assertRaises(ValueError):
            me0.validate_contract(contract)

    def test_cap_r_alias_to_eng_r_is_rejected(self):
        successor_map = me0.load_json(me0.SUCCESSOR_MAP_PATH)
        eng_r = next(x for x in successor_map["successor_roles"] if x["role_id"] == "ENG-R")
        eng_r["must_not_alias"] = []
        with self.assertRaises(ValueError):
            me0.validate_successor_map(successor_map)

    def test_cash_as_engine_is_rejected(self):
        contract = me0.load_json(me0.CONTRACT_PATH)
        contract["book_roles"]["BOOK-CASH"]["is_return_engine"] = True
        with self.assertRaises(ValueError):
            me0.validate_contract(contract)

    def test_silent_thesis_migration_is_rejected(self):
        contract = me0.load_json(me0.CONTRACT_PATH)
        contract["migration_invariants"].remove("NO_SILENT_THESIS_MIGRATION")
        with self.assertRaises(ValueError):
            me0.validate_contract(contract)

    def test_trading_authority_is_rejected(self):
        contract = me0.load_json(me0.CONTRACT_PATH)
        contract["governance"]["buy_sell_hold_authority"] = True
        with self.assertRaises(ValueError):
            me0.validate_contract(contract)

    def test_future_object_implementation_authority_is_rejected(self):
        successor_map = me0.load_json(me0.SUCCESSOR_MAP_PATH)
        mutated = copy.deepcopy(successor_map)
        mutated["future_object_identities"][0]["implementation_authority_in_ME0"] = True
        with self.assertRaises(ValueError):
            me0.validate_successor_map(mutated)


if __name__ == "__main__":
    unittest.main()
