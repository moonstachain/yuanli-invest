import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'yci0_rp1_financing_dgs10_archive.py'
spec = importlib.util.spec_from_file_location('dgs10_archive', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SAMPLE = b'''observation_date,DGS10\n2026-04-29,4.42\n2026-04-30,4.40\n2026-05-28,4.45\n2026-05-29,4.45\n2026-06-29,4.38\n2026-06-30,4.44\n2026-07-30,4.68\n2026-07-31,4.75\n'''

def test_extracts_frozen_complete_month_end_points():
    rows = module.extract_month_end_points(SAMPLE)
    assert [(r['month_end'], r['observation_date'], r['value_pct']) for r in rows] == [
        ('2026-04-30','2026-04-30',4.40),
        ('2026-05-31','2026-05-29',4.45),
        ('2026-06-30','2026-06-30',4.44),
        ('2026-07-31','2026-07-31',4.75),
    ]

def test_missing_required_month_fails_closed():
    with pytest.raises(RuntimeError, match='missing complete-month observation'):
        module.extract_month_end_points(SAMPLE.replace(b'2026-07-30,4.68\n2026-07-31,4.75\n', b''))
