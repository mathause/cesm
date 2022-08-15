from glob import glob

import numpy as np
from xarray import concat, open_dataset
from xarray.coding.times import decode_cf_datetime


def read_netcdfs(files, dim, transform_func=None, **kwargs):
    """read and combine multiple netcdf files

    Parameters
    ----------
    files : string or list of files
        path with wildchars or iterable of files
    dim : string
        dimension along which to combine, does not have to exist in
        file (e.g. ensemble)
    transform_func : function
        function to apply for individual datasets, see example
    **kwargs : keyword arguments
        passed to open_dataset

    Returns
    -------
    combined : xarray Dataset
        the combined xarray Dataset with transform_func applied

    Examples
    --------
    read_netcdfs('/path/*.nc', dim='ens', transform_func=lambda ds: ds.mean())

    References
    ----------
    http://xarray.pydata.org/en/stable/io.html#combining-multiple-files
    """

    def process_one_path(path):
        with open_dataset(path, **kwargs) as ds:
            if transform_func is not None:
                ds = transform_func(ds)

            ds.load()
            return ds

    if isinstance(files, str):
        paths = sorted(glob(files))
    else:
        paths = files

    datasets = [process_one_path(p) for p in paths]
    combined = concat(datasets, dim)
    return combined


def read_netcdfs_cesm(files, dim, transform_func=None, **kwargs):
    """read and combine multiple netcdf files with open_cesm

    Parameters
    ----------
    files : string or list of files
        path with wildchars or iterable of files
    dim : string
        dimension along which to combine, does not have to exist in
        file (e.g. ensemble)
    transform_func : function
        function to apply for individual datasets, see example
    **kwargs : keyword arguments
        passed to open_cesm

    Returns
    -------
    combined : xarray Dataset
        the combined xarray Dataset with transform_func applied

    Examples
    --------
    read_netcdfs('/path/*.nc', dim='ens', transform_func=lambda ds: ds.mean())

    References
    ----------
    http://xarray.pydata.org/en/stable/io.html#combining-multiple-files
    """

    def process_one_path(path):

        with open_cesm(path, **kwargs) as ds:
            if transform_func is not None:
                ds = transform_func(ds)
            ds.load()
            return ds

    if isinstance(files, str):
        paths = sorted(glob(files))
    else:
        paths = files

    datasets = [process_one_path(p) for p in paths]
    combined = concat(datasets, dim)
    return combined


def _wrap360(self, lon="lon"):
    """
    wrap longitude coordinates to 0..360
    Parameters
    ----------
    ds : Dataset
        object with longitude coordinates
    lon : string
        name of the longitude ('lon', 'longitude', ...)
    Returns
    -------
    wrapped : Dataset
        Another dataset array wrapped around.
    """

    # wrap -180..179 to 0..359

    new_lon = np.mod(self[lon], 360)

    self = self.assign_coords(**{lon: new_lon})
    # sort the data
    return self.reindex(**{lon: np.sort(self[lon])})


def _wrap180(self, lon="lon"):
    """
    wrap longitude coordinates to -180..180
    Parameters
    ----------
    ds : Dataset
        object with longitude coordinates
    lon : string
        name of the longitude ('lon', 'longitude', ...)
    Returns
    -------
    wrapped : Dataset
        Another dataset array wrapped around.
    """

    # wrap 0..359 to -180..179
    new_lon = self[lon].data

    # only modify values > 180
    sel = new_lon > 180

    if np.any(sel):
        # 359 -> -1, 181 -> -179
        new_lon[sel] = np.mod(new_lon[sel], -180)
        self = self.assign_coords(**{lon: new_lon})
        # sort the data

    self = self.reindex(**{lon: np.sort(self[lon])})

    return self


def _cos_wgt(self, lat="lat"):
    """cosine-weighted latitude"""
    return np.cos(np.deg2rad(self[lat]))


def open_cesm(
    filename_or_obj,
    *,
    round_latlon=4,
    interpolate_time=True,
    **kwargs,
):
    """Load and decode a dataset from a file or file-like object.
    Parameters
    ----------
    filename_or_obj : str, Path, file-like or DataStore
        Strings and Path objects are interpreted as a path to a netCDF file
        or an OpenDAP URL and opened with python-netCDF4, unless the filename
        ends with .gz, in which case the file is gunzipped and opened with
        scipy.io.netcdf (only netCDF3 supported). Byte-strings or file-like
        objects are opened by scipy.io.netcdf (netCDF3) or h5py (netCDF4/HDF).
    round_latlon : int, default : True
        The latitude and longitude coordinates are rounded to this number of
        decimals. This is done because there are very small numerical differences
        in the coordinates between the land and atmosphere files.
    interpolate_time : bool, default: True
        CESM writes the timestamp as the very last instance of the simulation interval.
        This means that the time is off by one day. If `interpolate_time` is True,
        this is fixed by calculating the time as the mean of the time bounds.
    **kwargs: mapping
        Keyword arguments passed on to xr.open_dataset

    Returns
    -------
    dataset : Dataset
        The newly created dataset.

    See Also
    --------
    open_mfdataset

    """

    decode_cf = kwargs.pop("decode_cf")
    decode_times = kwargs.pop("decode_times")

    # always open with decode_times = False
    ds = open_dataset(
        filename_or_obj,
        decode_cf=decode_cf,
        decode_times=False,
        **kwargs,
    )

    if interpolate_time:
        if "time_bnds" in ds.variables.keys() or "time_bounds" in ds.variables.keys():
            time_name = "time"

            if "time_bnds" in ds.variables.keys():
                time = ds.time_bnds.mean(axis=1)
            else:
                time = ds.time_bounds.mean(axis=1)

            if decode_cf is not False and decode_times is not False:
                units = ds.coords[time_name].units
                calendar = ds.coords[time_name].calendar
                time = decode_cf_datetime(time, units, calendar)

            ds = ds.assign_coords({time_name: time})

    if round_latlon:
        lon_name, lat_name = "lon", "lat"
        ds.coords[lon_name] = np.round(ds[lon_name], round_latlon)
        ds.coords[lat_name] = np.round(ds[lat_name], round_latlon)

    return ds
