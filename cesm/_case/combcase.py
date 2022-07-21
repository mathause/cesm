#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Mathias Hauser
# Date:

from .case import case


class combcase(object):
    """combining two associated CESM cases

    Given you have two seperate CESM simulations that belong
    together. For example a run is split into the historical period
    (hist) and a projection (proj).
    """

    def __init__(
        self,
        metaname,
        ens=None,
        suffix_hist="_hist",
        suffix_proj="_rcp8",
        cesm_cases_path="~/cesm_cases.yaml",
    ):

        """
        Parameters
        ==========
        metaname : str
            Part of the name both cases have in common. For example ref.
        ens : int | None
            Select the ensemble number of the registered cases.
        suffix_hist : str
            Suffix appended to the metaname, such that it builds the full
            case_name of the case. For example _hist -> ref_hist.
        suffix_proj : str
            Suffix appended to the metaname, such that it builds the full
            case_name of the case. For example _rcp8 -> ref_rcp8.
        cesm_cases_path : string
            Path and name of the cesm_cases file.
            Default: ~/cesm_cases.yaml.
        """

        super(combcase, self).__init__()
        self.metaname = metaname
        self._ens = ens
        self._suffix_hist = suffix_hist
        self._suffix_proj = suffix_proj

        self._cesm_cases_path = cesm_cases_path

        self._case_name_hist = self.__combine_name__(metaname, suffix_hist)
        self._case_name_proj = self.__combine_name__(metaname, suffix_proj)

        self._hist = None
        self._proj = None

    def __call__(self, suff, comp=None, hist=None):
        if comp is None:
            return self[suff]
        else:
            return self[suff](comp, hist)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        msg = "Combined CESM Cases: {}\nhist: {}\nproj: {}"
        msg = msg.format(self.metaname, self._case_name_hist, self._case_name_proj)
        return msg

    @property
    def hist(self):
        if self._hist is None:
            self._hist = case(self._case_name_hist, self._ens, self._cesm_cases_path)
        return self._hist

    @property
    def proj(self):
        if self._proj is None:
            self._proj = case(self._case_name_proj, self._ens, self._cesm_cases_path)
        return self._proj

    @staticmethod
    def __combine_name__(metaname, suffix):
        return metaname + suffix
