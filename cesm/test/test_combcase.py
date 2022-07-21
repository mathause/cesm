import unittest

import cesm_cases_yaml

import cesm

cesm_cases_path = "./test_cesm_cases.yaml"
case_name = "test_combcase"

case = cesm.combcase("test_combcase", cesm_cases_path=cesm_cases_yaml.string)


class TestCase_Cls(unittest.TestCase):
    def test_access_hist_proj__call__(self):
        self.assertEqual(case.hist, case("hist"))
        self.assertEqual(case.proj, case("proj"))

    def test_access_hist_proj__getitem__(self):
        self.assertEqual(case.hist, case["hist"])
        self.assertEqual(case.proj, case["proj"])

    def test_access_hist_proj_call_comp(self):
        self.assertEqual(case.hist.atm, case("hist", "atm"))
        self.assertEqual(case.hist.lnd, case("hist", "lnd"))
        self.assertEqual(case.hist.ocn, case("hist", "ocn"))
        self.assertEqual(case.hist.ice, case("hist", "ice"))

        self.assertEqual(case.proj.atm, case("proj", "atm"))
        self.assertEqual(case.proj.lnd, case("proj", "lnd"))
        self.assertEqual(case.proj.ocn, case("proj", "ocn"))
        self.assertEqual(case.proj.ice, case("proj", "ice"))

    def test_access_hist_proj_call_comp_hist(self):
        self.assertEqual(case.hist.atm.h0, case("hist", "atm", "h0"))
        self.assertEqual(case.hist.lnd.h0, case("hist", "lnd", "h0"))
        self.assertEqual(case.hist.ocn.h, case("hist", "ocn", "h"))
        self.assertEqual(case.hist.ice.h, case("hist", "ice", "h"))


if __name__ == "__main__":
    unittest.main(buffer=True)
