#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Author: Mathias Hauser
#Date: 

import numpy as np


class _data(object):

    """docstring for _data"""

    def __init__(self, h0):
        super(_data, self).__init__()

        self._h0 = h0
        self._lat_name = 'lat'
        self._lon_name = 'lon'

        self.filename = h0[0]

        self._weight = None
        self._lat = None
        self._lon = None

    @property
    def lat(self):
        return self.__get_prop__('_lat', self._lat_name)

    @property
    def lon(self):
        return self.__get_prop__('_lon', self._lon_name)

    # weight is special
    @property
    def weight(self):
        if self._weight is None:
            self._weight = CosWgt(self.lat)
        return self._weight

    def __get_prop__(self, name, varname):
        # only load data if required
        if getattr(self, name) is None:
            setattr(self, name, self.__get_data__(varname))
        return getattr(self, name)

    def __get_data__(self, varname):
        import xarray as xr
        return xr.open_cesm(self.filename)[varname]

# =============================================================================


class _data_lnd(_data):

    """docstring for _data_land"""

    def __init__(self, h0):
        super(_data_lnd, self).__init__(h0)

        self._area = None
        self._landfrac = None
        self._landmask = None

        self._DZSOI = None
        self._ZSOI = None

    @property
    def area(self):
        return self.__get_prop__('_area', 'area')

    @property
    def landfrac(self):
        return self.__get_prop__('_landfrac', 'landfrac')

    @property
    def landmask(self):
        return self.__get_prop__('_landmask', 'landmask')

    @property
    def DZSOI(self):
        return self.__get_prop__('_DZSOI', 'DZSOI')

    @property
    def ZSOI(self):
        return self.__get_prop__('_ZSOI', 'ZSOI')

# =============================================================================


class _data_atm(_data):
    """docstring for _data_land"""
    def __init__(self, h0):
        super(_data_atm, self).__init__(h0)
    
        self._landfrac = None
        self._hyam = None
        self._hybm = None
        self._hyai = None
        self._hybi = None

        self._P0 = None

    @property
    def landfrac(self):
        return self.__get_prop__('_landfrac', 'LANDFRAC').isel(time=0)

    @property
    def hyam(self):
        """hybrid B coefficient at layer midpoints
        """
        return self.__get_prop__('_hyam', 'hyam')

    @property
    def hybm(self):
        """hybrid B coefficient at layer midpoints
        """
        return self.__get_prop__('_hybm', 'hybm')

    @property
    def hyai(self):
        """hybrid A coefficient at layer interfaces
        """
        return self.__get_prop__('_hyai', 'hyai')

    @property
    def hybi(self):
        """hybrid B coefficient at layer interfaces
        """
        return self.__get_prop__('_hybi', 'hybi')

    @property
    def P0(self):
        return self.__get_prop__('_P0', 'P0')





# =============================================================================


def CosWgt(lat):
    """cosine-weighted latitude"""
    return np.cos(np.deg2rad(lat))
