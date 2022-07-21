import unittest

import cesm_cases_yaml

import cesm

case_name = "test_case"

case = cesm.case(case_name, cesm_cases_path=cesm_cases_yaml.string)

atm = case.atm
lnd = case.lnd
ocn = case.ocn
ice = case.ice


class TestCase_Cls(unittest.TestCase):
    def test_comp_access_hist__call__(self):
        self.assertEqual(atm.h0, atm("h0"))
        self.assertEqual(lnd.h0, lnd("h0"))
        self.assertEqual(ocn.h, ocn("h"))
        self.assertEqual(ice.h, ice("h"))

    def test_comp_access_hist__call__number_string_(self):
        self.assertEqual(atm.h0, atm("0"))

    def test_comp_access_hist__call__number_int_(self):
        self.assertEqual(atm.h0, atm(0))

    def test_comp_access_hist__getitem__(self):
        self.assertEqual(atm.h0, atm["h0"])
        self.assertEqual(lnd.h0, lnd["h0"])
        self.assertEqual(ocn.h, ocn["h"])
        self.assertEqual(ice.h, ice["h"])

    def test_comp_access_hist__getitem__number_string_(self):
        self.assertEqual(atm.h0, atm["0"])

    def test_comp_access_hist__getitem__number_int_(self):
        self.assertEqual(atm.h0, atm[0])


if __name__ == "__main__":
    unittest.main(buffer=True)
