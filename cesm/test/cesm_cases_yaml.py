import os

# determine the location of this file
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


string = """
# INVALID CASE: the folder of the case does not exist
test_case_no_folder:
  folder: {location}
  name: i.e122.ICRU.hcru_hcru.no_folder-io192.001

# INVALID CASE
test_case_no_comp_folder:
    folder: {location}
    name: i.e122.ICRU.hcru_hcru.no_comp_folder-io192.001

# INVALID CASE
test_case_post_name_missing:
    folder_hist: {location}
    folder_post: {location}
    name: b.e122.B2000.f19_g16.test-io192.001

# VALID CASE: SIMPLE
test_case:
    folder: {location}
    name: b.e122.B2000.f19_g16.test-io192.001

# VALID CASE: post and hist folder 
test_case_post:
    folder_hist: '{location}/{name}'
    folder_post: '{location}/post/{name}'
    name: b.e122.B2000.f19_g16.test-io192.001


# ENSEMBLE with 2 members
test_case_ens:
    -   folder: {location}
        name: b.e122.B2000.f19_g16.test-io192.001
    -   folder: {location}
        name: b.e122.B2000.f19_g16.test-io192.001


# COMBCASE

# VALID CASE: hist
test_combcase_hist:
    folder: {location}
    name: b.e122.B2000.f19_g16.test-io192.001

# VALID CASE: proj
test_combcase_rcp8:
    folder: {location}
    name: b.e122.B2000.f19_g16.test-io192.001

""".format(
    location=__location__, name="{name}"
)
