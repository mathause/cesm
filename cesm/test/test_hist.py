import unittest

import cesm_cases_yaml

import cesm

cesm_cases_path = "./test_cesm_cases.yaml"
case_name = "test_case"

case = cesm.case(case_name, cesm_cases_path=cesm_cases_yaml.string)


class TestCase_Cls(unittest.TestCase):

    # def test_hist_folder_post(self):

    #     f = './b.e122.B2000.f19_g16.test-io192.001/ocn/post'
    #     self.assertEqual(case.ocn, )
    #     self.assertEqual(case.proj, case('proj'))

    def test(self):
        pass


if __name__ == "__main__":
    unittest.main(buffer=True)
