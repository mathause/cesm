import os

import cesm
import cesm_cases_yaml

__folder__ = cesm_cases_yaml.__location__

def filename(name, comp, suffix):
    # e.g.: ./b.e122.B2000.f19_g16.test-io192.001/atm/hist
    
    return os.path.join(__folder__, name, comp, suffix)


case_name = 'test_case'

case = cesm.case(case_name, cesm_cases_path=cesm_cases_yaml.string)

atm = case.atm
lnd = case.lnd
ocn = case.ocn
ice = case.ice

def test_comb_atm_folder_hist():
    f = filename('b.e122.B2000.f19_g16.test-io192.001', 'atm', 'hist')
    assert atm.folder_hist == f

def test_comb_atm_folder_post():
    f = filename('b.e122.B2000.f19_g16.test-io192.001', 'atm', 'post')
    assert atm.folder_post == f

def test_comb_lnd_folder_hist():
    f = filename('b.e122.B2000.f19_g16.test-io192.001', 'lnd', 'hist')
    assert lnd.folder_hist == f

def test_comb_lnd_folder_post():
    f = filename('b.e122.B2000.f19_g16.test-io192.001', 'lnd', 'post')
    assert lnd.folder_post == f

def test_comb_ocn_folder_hist():
    f = filename('b.e122.B2000.f19_g16.test-io192.001', 'ocn', 'hist')
    assert ocn.folder_hist == f

def test_comb_ocn_folder_post():
    f = filename('b.e122.B2000.f19_g16.test-io192.001', 'ocn', 'post')
    assert ocn.folder_post == f

def test_comb_ice_folder_hist():
    f = filename('b.e122.B2000.f19_g16.test-io192.001', 'ice', 'hist')
    assert ice.folder_hist == f

def test_comb_ice_folder_post():
    f = filename('b.e122.B2000.f19_g16.test-io192.001', 'ice', 'post')
    assert ice.folder_post == f
