#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Mathias Hauser
# Date:

from __future__ import division


import os
import numpy as np
import yaml

import glob
import weakref

from .comp import _lnd, _atm, _ice


def print_casenames(cesm_cases_path='~/cesm_cases.yaml'):
    """pretty print all case names

        Parameters
        ----------
        cesm_cases_path : string
            Path and name of the cesm_cases file.
            Default: ~/cesm_cases.yaml.

    """

    casedefs = __read_yaml__(cesm_cases_path)
    print("Availiable cases:")
    print(__print_casenames__(casedefs))

# -----------------------------------------------------------------------------


def __print_casenames__(casedefs):
    """loop cases for pretty print"""

    msg = ""
    ens = False
    for casename in sorted(casedefs.keys()):
        if __is_ensemble__(casedefs[casename]):
            msg += casename + "*\n"
            ens = True
        else:
            msg += casename + "\n"

    if ens:
        msg += "\n* denotes ensembles"

    return msg

# -----------------------------------------------------------------------------


def __is_ensemble__(case):
    """check if case is registered as ensemble in the yaml file"""

    return isinstance(case, list)

# =============================================================================


class case(object):

    """A case is a cesm simulation."""

    def __init__(self, case_name, ens=None, cesm_cases_path='~/cesm_cases.yaml'):
        """
        Parameters
        ==========
        case_name : string
            One of the cases registered in the cesm_cases file.
        ens : int | None
            Select the ensemble number of the registered cases.
        cesm_cases_path : string
            Path and name of the cesm_cases file.
            Default: ~/cesm_cases.yaml.
        """


        super(case, self).__init__()
        self.case_name = case_name

        self.cesm_cases_path = cesm_cases_path
        self.casedef = __parse_yaml__(case_name, ens, cesm_cases_path)

        # check something exists at this location        
        if not os.path.isdir(self.casedef['folder_hist']):
            folder = self.casedef['folder_hist']
            msg = "There is nothing at: '{}'".format(folder)
            raise RuntimeError(msg)

        # organize _comp as a property
        self._atm = None
        self._lnd = None
        self._ice = None

        # add DATA
        # print self.atm
        # if self.atm is not None:
        #     self._atm_data = _data_atm(self.atm.__dict__.get('h0', None))
        # self._lnd_data = _data_lnd(self.lnd.__dict__.get('h0', None))

        # self.atm.data = self._atm_data
        # self.lnd.data = self._lnd_data

        # for h in self.atm._hist_unique:
        #     if self.atm:
        #         getattr(self.atm, 'h' + str(h))._atm_data = self._atm_data
        #     getattr(self.atm, 'h' + str(h))._lnd_data = self._lnd_data

        # for h in self.lnd._hist_unique:
        #     if self.atm:
        #         getattr(self.lnd, 'h' + str(h))._atm_data = self._atm_data
        #     getattr(self.lnd, 'h' + str(h))._lnd_data = self._lnd_data


    def __repr__(self):
        msg = "CESM Case: {}\nfolder_hist: {}\nfolder_post: {}"
        msg = msg.format(self.case_name, self.casedef['folder_hist'], self.casedef['folder_post'])
        return msg


    @property
    def atm(self):
        if self._atm is None:
            self._atm = _atm(self, 'cam')
        return self._atm

    @property
    def lnd(self):
        if self._lnd is None:
            self._lnd = _lnd(self, 'clm2')
        return self._lnd

    @property
    def ice(self):
        if self._ice is None:
            self._ice = _ice(self, 'cice')
        return self._ice  

# =============================================================================


def __read_yaml__(path):
    """read the cesm_case file

        Parameters
        ==========
        path : string
            Full name of the yaml file. May contain '~', expanded to home.
    """

    path = os.path.expanduser(path)
    with open(path, 'r') as stream:
        return yaml.load(stream)


def __parse_yaml__(case_name, ens, cesm_cases_path):
    """
    parse the cesm_case yaml file
    """

    # read yaml file
    casedefs = __read_yaml__(cesm_cases_path)

    # case exists?
    casedef = casedefs.get(case_name, None)

    if casedef is None:
        print_casenames()
        msg = ("'{}' is not known. See above.".format(case_name))
        raise KeyError(msg)

    # check if it is a ensemble
    if __is_ensemble__(casedef):
        # check if ens is a valid ensemble member
        if ens not in range(len(casedef)):
            msg = ("'{case}' is an ensemble."
                   " Specify 'ens' in the range of 0 to {ncases}".
                   format(case=case_name, ncases=len(case) - 1))
            raise KeyError(msg)

        casedef = casedef[ens]


    if 'resolution' not in casedef.keys():
        casedef['resolution'] = 'f19_g16'

    casedef['case_name'] = case_name

    casedef['folder_hist'] = __create_folder_name__(casedef, 'hist')
    casedef['folder_post'] = __create_folder_name__(casedef, 'post')

    return casedef


def __create_folder_name__(casedef, suffix):
    """get folder path"""

    # is folder_post or folder_hist saved?
    folder = casedef.get('folder_' + suffix, None)
    case_name = casedef['name']

    # construct path
    if folder:
        path = folder.format(name=case_name)
    else:
        folder = casedef['folder']
        path = os.path.join(folder, case_name)

    return path







# =============================================================================


