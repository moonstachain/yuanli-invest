import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class R22ReFoundationTests(unittest.TestCase):
 def test_state(self):
  p=json.loads((ROOT/'packages/contracts/schemas/vnext/research-state-vector.schema.json').read_text())['properties']; self.assertTrue(all(k in p for k in ('P','Xs','N','V','Xa','Xp','S'))); self.assertTrue(p['scalar_pnx_score_prohibited']['const'])
 def test_receipt(self):
  p=json.loads((ROOT/'packages/contracts/schemas/vnext/execution-receipt.schema.json').read_text())['properties']; self.assertFalse(p['live_execution_authorized']['const'])
 def test_projection(self):
  s=json.loads((ROOT/'docs/architecture/CANON-STATUS.json').read_text()); self.assertEqual(s['projection_semantics'],'deterministic_non_authoritative_projection'); self.assertEqual(s['stages']['R2_1']['status'],'accepted_merged')
if __name__=='__main__': unittest.main()
