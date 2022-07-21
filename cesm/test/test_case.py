import tempfile
import unittest

import cesm_cases_yaml

import cesm

# cesm_cases_path = './cesm_cases_test.yaml'


class TestCase_Cls(unittest.TestCase):
    def test_case_not_existing_folder(self):
        # test case has no folder at the correct place

        case_name = "test_case_no_folder"
        self.assertRaises(
            RuntimeError,
            cesm.case,
            case_name=case_name,
            cesm_cases_path=cesm_cases_yaml.string,
        )

    def test_case_not_in_yaml_file(self):
        # test case does not exist in yaml file
        case_name = "test_case_missing"

        self.assertRaises(
            KeyError,
            cesm.case,
            case_name=case_name,
            cesm_cases_path=cesm_cases_yaml.string,
        )

    def test_case_no_comp_folder(self):
        # folder exists but has no subfolders
        case_name = "test_case_no_comp_folder"
        case = cesm.case(case_name, cesm_cases_path=cesm_cases_yaml.string)

        with self.assertRaises(OSError):
            case.atm

    def test_case_post_no_name(self):
        # folder_post or folder_hist must include {name}

        case_name = "test_case_post_name_missing"
        self.assertRaises(
            RuntimeError,
            cesm.case,
            case_name=case_name,
            cesm_cases_path=cesm_cases_yaml.string,
        )

    def test_case_cesm_cases_yaml_missing(self):

        cesm_cases_path_temp = tempfile.mktemp(".yaml")

        self.assertRaises(
            IOError, cesm.case, case_name="test", cesm_cases_path=cesm_cases_path_temp
        )


if __name__ == "__main__":
    unittest.main(buffer=True)
