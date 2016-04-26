#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Author: Mathias Hauser
#Date: 

import numpy as np
import warnings

from .post import post_cls

class _hist(object):

    """subset history streams"""

    def __init__(self, hist, filename, fullname, year, month, day, second,
                 folder_post, case, modname):

        super(_hist, self).__init__()

        self.hist = hist

        self._filename = filename
        self._fullname = fullname
        self.year = year
        self.month = month
        self.day = day
        self.second = second
        self.folder_post = folder_post
        self._case = case
        self.casedef = case.casedef
        self._modname = modname
        self.post = post_cls(folder_post, case.casedef, hist, modname)

        # stop infinite recursion
        self.__lnd_data = None
        self.__atm_data = None

    @property
    def _lnd_data(self):
        if self.__lnd_data is None:
            self.__lnd_data = self._case.lnd._lnd_data
        return self.__lnd_data
    
    @property
    def _atm_data(self):
        if self.__atm_data is None:
            self.__atm_data = self._case.atm._atm_data
        return self.__atm_data

    def __getitem__(self, key):
        out = self._fullname[key].tolist()

        if len(out) == 1:
            return out[0]
        else:
            return out


    @property
    def filename(self):
        """List of all history file names (name.nc)"""
        return self._filename.tolist()

    @property
    def fullname(self):
        """List of all history files (path/name.nc)"""
        return self[:]

    def _get_sel(self, year=None, month=None, day=None, second=None, last=True):
        """
        Subset history files. Returns boolean array.

        Parameters
        ==========
        year : None | int | slice
            Select year. See below.
        month : None | int | slice
            Select month. See below.
        day : None | int | slice
            Select day. See below.
        second : None | int | slice
            Select second. See below.

        Returns
        =======
        sel : array of bool

        ..Note::
          None makes no selection.
          int select exclusively this number.
          slice(start, end) selects range (inclusive).


        """

        # all True
        sel = np.ones_like(self.year, dtype=np.bool)

        # select
        sel = self.__get_sel_single__(sel, self.year, year)
        sel = self.__get_sel_single__(sel, self.month, month)
        sel = self.__get_sel_single__(sel, self.day, day)
        sel = self.__get_sel_single__(sel, self.second, second)

        if not last:
            sel[-1] = False

        if not np.any(sel):
            msg = "sel is empty. Nothing selected."
            warnings.warn(msg, RuntimeWarning)

        return sel

    def sel(self, year=None, month=None, day=None, second=None, last=True):
        """
        Returns all or a subset history file names.

        Parameters
        ==========
        year : None | int | slice
            Select year. See below.
        month : None | int | slice
            Select month. See below.
        day : None | int | slice
            Select day. See below.
        second : None | int | slice
            Select second. See below.

        Returns
        =======
        filename : string or list of strings

        ..Note::
          None makes no selection.
          int select exclusively this number.
          slice(start, end) selects range (inclusive).


        """

        sel = self._get_sel(year, month, day, second, last)

        return self[sel]


    @staticmethod
    def __get_sel_single__(sel, data, condition):
        """
        get selection for every single condition (year, month, day)

        """

        # no selection
        if condition is None:
            return sel

        # select with a slice
        if isinstance(condition, slice):
            if condition.step:
                raise ValueError("step can not be set")

            if condition.start:
                sel = (sel) & (data >= condition.start)

            if condition.stop:
                sel = (sel) & (data <= condition.stop)

            return sel

        # select with a single condition
        return (sel) & (data == condition)