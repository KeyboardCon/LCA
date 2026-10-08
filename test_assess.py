import unittest
from pathlib import Path
from unittest.mock import patch

import assess


class AssessmentChecks(unittest.TestCase):
    def test_archived_method_has_fossil_co2_factor_one(self):
        dataset = Path("/workspace/tiangong-data/tiangong_lca_data")
        factors, _ = assess.factors(dataset)
        self.assertEqual(factors["08a91e70-3ddc-11dd-923d-0050c2490048"], 1)

    def test_missing_mass_fails_before_calculation(self):
        original = assess.read_csv

        def changed(path):
            rows = original(path)
            if path.name == "bom.csv":
                rows[0]["mass_g"] = "185"
            return rows

        with patch.object(assess, "read_csv", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "mass check"):
                assess.assess(Path("/workspace/tiangong-data/tiangong_lca_data"))

    def test_real_dataset_keeps_incomplete_total_null(self):
        result = assess.assess(Path("/workspace/tiangong-data/tiangong_lca_data"))
        self.assertIsNone(result["gwp100_total_kg_co2e"])
        self.assertEqual(result["total_finished_mass_g"], "860.80")
        self.assertGreater(result["unmatched_materials"], 0)


if __name__ == "__main__":
    unittest.main()
