import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "superpowers" / "specs" / "2026-08-21-qxm-f-financial-mechanics-capability-closure-design.md"
PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-08-21-qxm-f-financial-mechanics-capability-closure.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


try:
    from scripts.validate_qxm_f_closure import (
        LEGAL_STATES,
        assert_no_authority_escalation,
        assert_state,
        validate_qxm_f,
    )
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "QXM-F validator missing as expected in RED; "
        f"approved_spec_sha256={sha256(SPEC)}; "
        f"approved_plan_sha256={sha256(PLAN)}"
    ) from exc


class QXMFClosureBootstrapTests(unittest.TestCase):
    def test_state_enum_is_closed(self):
        for state in LEGAL_STATES:
            assert_state(state)
        with self.assertRaises(AssertionError):
            assert_state("G1_MAGIC_AUTO_ADMISSION")

    def test_trading_and_silent_authority_escalation_fail_closed(self):
        assert_no_authority_escalation({
            "registry_admission_authorized": False,
            "benchmark_execution_authorized": False,
            "trading_action_authorized": False,
        })
        with self.assertRaises(AssertionError):
            assert_no_authority_escalation({"trading_action_authorized": True})
        with self.assertRaises(AssertionError):
            assert_no_authority_escalation({"capability_promotion_authorized": True})

    def test_full_bootstrap_validates(self):
        result = validate_qxm_f(ROOT)
        self.assertEqual(result["stage"], "QXM_F_FINANCIAL_MECHANICS_CAPABILITY_CLOSURE")


if __name__ == "__main__":
    unittest.main()
