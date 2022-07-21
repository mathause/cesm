#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Mathias Hauser
# Date:

import os
import re
import warnings

import numpy as np

from .data import _data_atm, _data_lnd
from .hist import _hist
from .post import post_cls


class _comp(object):

    """CLASS for CESM Model COMPONENTS (lnd, atm, ...)"""

    def __init__(self, case, modname, comp):

        super(_comp, self).__init__()

        self._case = case
        self.casedef = case.casedef
        self._modname = modname
        self.comp = comp

        self.folder_hist = self.__folder_hist__()
        self.folder_post = self.__folder_post__()

        self._re_str = self.__get_re_string__()
        self._hist_unique = None

        self.has_histfiles = False

        self.__parse_hist_files__()

        self.__atm_data = None
        self.__lnd_data = None

        self.post = post_cls(
            self.folder_post, case.casedef, "no_hist", modname, add_hist=False
        )

    def __repr__(self):
        msg = "'{}' component of the CESM Case '{}'"
        msg = msg.format(self.comp, self.casedef["case_name"])
        return msg

    @property
    def _atm_data(self):

        if not self._case.atm.has_histfiles:
            raise RuntimeError("Has not atm histfiles.")

        if self._case.atm.__atm_data is None:
            self.__atm_data = _data_atm(getattr(self._case.atm, "h0", None))

        return self.__atm_data

    @property
    def _lnd_data(self):

        if not self._case.lnd.has_histfiles:
            raise RuntimeError("Has not lnd histfiles.")

        if self._case.lnd.__lnd_data is None:
            self.__lnd_data = _data_lnd(getattr(self._case.lnd, "h0", None))

        return self.__lnd_data

    def __call__(self, hist):
        return self[hist]

    def __getitem__(self, key):

        if isinstance(key, int):
            key = "h" + str(key)
            return getattr(self, key)

        return getattr(self, key)

    def __getattr__(self, key):
        """Error msg for history file requests"""

        # check if '0' or '1'
        if key.isdigit():
            key = "h" + key
            return getattr(self, key)

        if key.startswith("h"):
            msg = "No history files found for '{}'".format(key)
            raise AttributeError(msg)
        else:
            # default message
            msg = "'_comp' object has no attribute '{}'".format(key)
            raise AttributeError(msg)

    # =============================================================================

    def __folder__(self, suffix):
        """get folder path"""

        folder = self.casedef.get("folder_" + suffix, None)

        # /path/name/lnd/hist
        return os.path.join(folder, self.comp, suffix)

    # =========================================================================

    def __folder_hist__(self):
        """folder of history files"""
        return self.__folder__("hist")

    # =========================================================================

    def __folder_post__(self):
        """folder of postprocessed files"""
        return self.__folder__("post")

    # =========================================================================

    def __get_re_string__(self):
        """get regular expression string"""

        re_str = re.compile(
            r"^"
            + self.casedef["name"]  # beginning of word
            + "."  # name of run
            + self._modname
            + "."  # name of module
            + "(?P<hist>.*)."  # hist file name
            "(?P<year>\d{4})-"  #  year
            "(?P<month>\d{2})"  #  month
            "(.nc"  #  end
            "|-"  #  -- OR --
            "(?P<day>\d{2})"  #   day
            "(.nc"  #   end
            "|-"  #   -- OR --
            "(?P<second>\d{5})"  #   second
            ".nc))"  #   end
            "(?P<zip>.*)"  # is it zipped?
        )

        return re_str

    def __get_hist_files__(self):
        """obtain available history file"""
        return sorted(os.listdir(self.folder_hist))

        # files = sorted(glob.glob(self.folder_hist + '/*'))
        # return [os.path.basename(ff) for ff in files]

    def __parse_hist_files__(self):
        """read h0/ h1 year, month, etc. from hist files"""

        hfiles = self.__get_hist_files__()
        self.histfiles = hfiles

        # create empty lists
        filename, fullname, hist = [], [], []
        year, month, day, second = [], [], [], []

        is_zipped = ""
        for h in hfiles:

            # find files that match
            reg = self._re_str.search(h)

            if reg:

                filename.append(h)
                fullname.append(os.path.join(self.folder_hist, h))
                hist += [reg.group("hist").replace(".", "_")]
                year += [reg.group("year")]
                month += [reg.group("month")]

                # replace None
                day += [reg.group("day") if reg.group("day") else "1"]
                second += [reg.group("second") if reg.group("second") else "0"]

                if not is_zipped:
                    is_zipped = reg.group("zip")

            else:
                pass

        filename = np.array(filename)
        fullname = np.array(fullname)
        hist = np.array(hist, dtype=np.str)
        year = np.array(year, dtype=np.int)
        month = np.array(month, dtype=np.int)
        day = np.array(day, dtype=np.int)
        second = np.array(second, dtype=np.int)

        # determine available history streams
        self._hist_unique = np.unique(hist).tolist()

        from .hist import _hist

        # add history stream as attribute
        for h in self._hist_unique:
            # all files that are from this given hist stream
            sel = hist == h
            # create individual hist class
            hist_class = _hist(
                h,
                filename[sel],
                fullname[sel],
                year[sel],
                month[sel],
                day[sel],
                second[sel],
                self.folder_post,
                self._case,
                self._modname,
                self.comp,
            )

            # add it as an attribute
            setattr(self, str(h), hist_class)

        if len(fullname):
            self.has_histfiles = True

        if is_zipped:
            msg = "{} is probably zipped (file ending: {})".format(self.comp, is_zipped)
            warnings.warn(msg)

    def sel(self, hist, year=None, month=None, day=None, second=None, last=True):

        # if isinstance(hist, int):
        #     hist = 'h' + str(hist)

        hist = getattr(self, hist)
        return hist.sel(year, month, day, second, last)


# -----------------------------------------------------------------------------


# subclass _comp for lnd and atm
class _lnd(_comp):

    """docstring for _lnd"""

    def __init__(self, case, modname):
        super(_lnd, self).__init__(case, modname, "lnd")

        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self._lnd_data

        return self._data


# -----------------------------------------------------------------------------


class _atm(_comp):

    """docstring for _atm"""

    def __init__(self, case, modname):
        super(_atm, self).__init__(case, modname, "atm")

    @property
    def data(self):
        if self._data is None:
            self._data = self._atm_data

        return self._data


# -----------------------------------------------------------------------------


class _ice(_comp):

    """docstring for _ice"""

    def __init__(self, case, modname):
        super(_ice, self).__init__(case, modname, "ice")


# -----------------------------------------------------------------------------


class _ocn(_comp):

    """docstring for _ocn"""

    def __init__(self, case, modname):
        super(_ocn, self).__init__(case, modname, "ocn")


# # sorted(glob.glob(case.case['folder'] + case.case['name'] + '/*/hist/*'))


# def globfiles(case):
#     sorted(glob.glob(case.case['folder'] + case.case['name'] + '/atm/hist/*'))
#     sorted(glob.glob(case.case['folder'] + case.case['name'] + '/glc/hist/*'))
#     sorted(glob.glob(case.case['folder'] + case.case['name'] + '/ice/hist/*'))
#     sorted(glob.glob(case.case['folder'] + case.case['name'] + '/lnd/hist/*'))
#     sorted(glob.glob(case.case['folder'] + case.case['name'] + '/rof/hist/*'))
