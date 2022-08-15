import multiprocessing as _multiprocessing
import os as _os

from cesm.utils import xarray_utils as xu

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats as _stats


def var(hist, varname, year, processes=1):

    source_files = _postprocess(
        hist, varname, year=year, force_save=False, check_age=False, processes=processes
    )

    return xu.read_netcdfs_cesm(source_files, "time")


# -----------------------------------------------------------------------------


def clim_monthly(hist, varname, year):

    ds = var(hist, varname, year)

    return ds.groupby("time.month").mean(dim="time")


# -----------------------------------------------------------------------------


def evapotranspiration(hist, varname="ET", year=None, processes=1):

    transform_func_internal = _trans_evapotranspiration

    # no varname required
    new_var = "ET"

    source_files = _postprocess(
        hist,
        varname,
        year=year,
        transform_func=transform_func_internal,
        force_save=False,
        check_age=False,
        processes=processes,
        new_var=new_var,
    )

    return xu.read_netcdfs_cesm(source_files, "time")


# -----------------------------------------------------------------------------


def soillev(hist, varname, year, transform_func=None):

    prefix = "soillev"
    transform_func_internal = _trans_soilliq_soillev

    fNs = _postprocess(
        hist,
        varname,
        year,
        prefix=prefix,
        transform_func=transform_func_internal,
        new_var=None,
        force_save=False,
        check_age=False,
    )

    return xu.read_netcdfs_cesm(fNs, "time", transform_func=transform_func)


# -----------------------------------------------------------------------------


def var_SREX_LAND(hist, varname, year, force_save=False, check_age=False):

    prefix = "SREX"
    transform_func = _trans_SREX_LAND_var

    fNs = _postprocess(
        hist,
        varname,
        year,
        prefix=prefix,
        transform_func=transform_func,
        new_var=None,
        force_save=force_save,
        check_age=check_age,
    )

    return xu.read_netcdfs_cesm(fNs, "time")


# -----------------------------------------------------------------------------


def annual_resample(hist, varname, year, apply_func="mean"):

    prefix = ["annual", apply_func]

    transform_func = _trans_annual_resample(apply_func)

    fNs = _postprocess(
        hist,
        varname,
        year,
        prefix=prefix,
        transform_func=transform_func,
        new_var=None,
        force_save=False,
        check_age=False,
    )

    return xu.read_netcdfs_cesm(fNs, "time")


# ======================================================================
# TRANSFORMATION FUNCTIONS
# ======================================================================


def _trans_extract_var(varname, hist):
    # extract a named variable
    def _inner(ds):
        return ds[varname]

    return _inner


# -----------------------------------------------------------------------------


def _trans_evapotranspiration(varname, hist):
    # evatranspiration is QSOIL + QVEGE + QVEGT
    def _inner(ds):
        return ds.QSOIL + ds.QVEGE + ds.QVEGT

    return _inner


# -----------------------------------------------------------------------------

# def _trans_soilliq(varname, hist):
#     # we only need the first 10 levels of SOILLIQ/ SOILICE
#     def _inner(ds):
#         return ds[varname].isel(levgrnd=slice(None, 10))
#     return _inner


# -----------------------------------------------------------------------------


def _trans_SREX_LAND_var(varname, hist):
    """
    calculate var for each SREX region and global land mean

    """

    # obtain necessary data
    import regionmask

    landfrac = hist.data.landfrac
    weight = hist.data.weight

    wgt = landfrac * weight
    mask = regionmask.defined_regions.srex.mask(landfrac, wrap_lon=True)

    abbrevs = ["global", "global_land", "global_land_wo_antarctica"]
    abbrevs += regionmask.defined_regions.srex.abbrevs

    # extract a named variable
    def _inner(ds):
        ds = ds[varname]

        # global mean
        ave = [ds.weighted(weight).mean(("lat", "lon"))]

        # global land mean
        a = ds.weighted(wgt).mean(("lat", "lon"))
        ave.append(a)

        # global land mean w/o antarctica
        d = ds.sel(lat=slice(-60, 87))
        a = d.weighted.mean(("lat", "lon"))
        ave.append(a)

        # srex mean
        for i in range(1, 27):
            a = ds.where(mask == i).weighted(wgt).mean(("lat", "lon"))

            ave.append(a)

        ds = xr.concat(ave, dim="srex")

        # shift srex coordinates such that 1 to 26 corresponds to the
        # regions
        x = np.arange(-2, 27)
        ds.srex.values[:] = x

        # add the name of the regions
        ds = ds.assign_coords(**{"srex_abbrev": ("srex", abbrevs)})

        return ds

    return _inner


# -----------------------------------------------------------------------------


def _trans_soilliq_soillev(varname, hist):
    """
    transformation function to extract SOILLIQ/ ICE in three levels

    split soil into three parts: 0 to 10 // 10 to 100 // 100 to 380 cm
    """

    def _inner(ds):

        # only the 10 first levels
        ds = ds[varname].isel(levgrnd=slice(None, 10))

        # split levgrnd
        soillev = pd.cut(ds.levgrnd, [0, 0.1, 1, 2.9])

        # add the new category
        ds = ds.assign_coords(soillev=("levgrnd", soillev))

        # take sum over the three parts
        ds = ds.groupby("soillev").sum(dim="levgrnd", skipna=False)

        # hack: turn pandas IntervalIndex to string
        # soillev = ds.soillev.values
        # soillev = [n.__str__() for n in soillev]
        soillev = ["(0, 0.1]", "(0.1, 1]", "(1, 2.9]"]
        ds.soillev.values[:] = soillev

        return ds

    return _inner


# -----------------------------------------------------------------------------


def _trans_annual_resample(apply_func):
    """
    transformation function to extract annual mean, max, etc.

    Parameters
    ----------
    apply_func : str
        Function applied to every year. E.g. 'mean', 'max', etc. See
        xarray's resample function.
    """

    def _trans_annual_resample_internal(varname, hist):
        def _inner(ds):

            ds = ds[varname]
            year = _stats.mode(ds["time.year"].values, keepdims=False).mode
            ds = ds.sel(time=str(year))
            resampler = ds.resample(time="A")
            ds = getattr(resampler, apply_func)(keep_attrs=True)

            return ds

        return _inner

    return _trans_annual_resample_internal


# =============================================================================


def _postprocess(
    hist,
    varname,
    year,
    prefix="",
    new_var=None,
    transform_func=_trans_extract_var,
    force_save=False,
    check_age=False,
    processes=1,
):
    """
    generic function postprocessing/ saving all selected cesm files

    Parameters
    ----------
    hist : cesm hist class
        Instance of the hist class from cesm package.
    varname : str
        Name of the variable.
    year : None | int | slice
        Select year. None makes no selection. int select exclusively
        this year. slice(start, end) selects range of year (inclusive).
    prefix : list of str
        Strings to prepend the name of the simulation (after the
        folder). See also _prefix function.
    new_var : string or None, optional
        New name for the variable, e.g. when saving ET.
    transform_func : function
        Function used to read and process the data.
    force_save : bool, optional
        If True, forces a (re-)save. Default: False.
    check_age : bool, optional
        Check if source_files are younger than dest_file. If so,
        re-save. Default: False.
    processes : int, optional
        For multiprocessing.

    Returns
    =======
    dest_files : list of strings
        List of all files that were selected.


    """

    if new_var is None:
        new_var = varname

    prefix = _prefix(prefix, new_var)

    # list of years we want to process
    years = np.unique(hist.year[hist._get_sel(year=year)])

    # first and last years
    yearmin, yearmax = np.min(years), np.max(years)

    # created destination files
    dest_files = []

    years_require_saving = []

    # loop years
    for year in years:

        # name of source and destination files
        source_files = hist.sel(year=year)
        dest_file = _destfile_name(hist, prefix, year)

        dest_files.append(dest_file)

        # do we need to save the file?
        if _maybe_save(source_files, dest_file, force_save, check_age):

            years_require_saving.append(year)

            # check that all files exist or error
            _check_all_files_exist(source_files)

    # loop only years that need to be saved
    if years_require_saving:
        n_years_require_saving = len(years_require_saving)
        print(str(n_years_require_saving) + " years require saving")

        # prepare for parallel processing
        all_args = list()
        for year in years_require_saving:

            msg = "writing variable: {} in {}..{}"
            msg = msg.format(year, yearmin, yearmax)

            # name of source and destination files
            source_files = hist.sel(year=year)
            dest_file = _destfile_name(hist, prefix, year)

            # pack arguments
            args = (
                source_files,
                dest_file,
                varname,
                hist,
                new_var,
                transform_func,
                msg,
            )

            # no multiprocessing
            if processes == 1:
                # save it
                _save_var(args)

            # multiprocessing
            else:
                all_args.append(args)

        # multiprocessing
        if processes > 1:
            pool = _multiprocessing.Pool(processes=processes)

            p = pool.map_async(_save_var, all_args)

            try:
                p.get(0xFFFF)
            except KeyboardInterrupt:
                print("parent received control-c")
                return

    return dest_files


def _destfile_name(hist, prefix, year):
    """
    construct the full name of the saved yearly file

    Parameters
    ----------
    hist : cesm hist class
        Instance of the hist class from cesm package.
    prefix : list of str
        Strings to prepend the name of the simulation (after the
        folder). See also _prefix function.
    year : integer
        Year which is read/ saved. Added as suffix.
    """

    return hist.post.pre_suf(prefix, str(year), prefix_folder=True)


def _prefix(prefix, varname):
    """
    parse prefix and add name of the variable

    Parameters
    ----------
    prefix : str
        Prefix appended to the name of the variable. Can be empty ('').
    varname : str
        Name of the variable.

    Returns
    -------
    prefix : list of str
        Concatenated list of varname and prefix.

    Examples
    --------
    >>> _prefix('', 'TS')
    ['TS']
    >>> _prefix('mean', 'TS')
    ['TS', 'mean']
    >>> _prefix(['mean'], 'TS')
    ['TS', 'mean']
    >>> _prefix(['mean', 'US'], 'TS')
    ['TS', 'mean', 'US']

    """

    # empty list if prefix is ''
    prefix = prefix if prefix != "" else []

    prefix = _str2lst(prefix)

    return [varname] + prefix


def _save_var(args):
    """
    save variable in annual files, one per variable
    """

    # unpack args
    (source_files, dest_file, varname, hist, new_var, transform_func, msg) = args

    print(msg)

    # read file(s) and maybe concatenate
    ds = xu.read_netcdfs_cesm(source_files, "time", transform_func(varname, hist))

    # maybe rename
    ds = ds.to_dataset(name=new_var)

    # save as yearly file
    ds.to_netcdf(dest_file, format="NETCDF4_CLASSIC")


def _maybe_save(source_files=None, dest_file=None, force_save=False, check_age=False):
    """
    determine if a file needs to be computed and saved

    Parameters
    ----------
    source_files : str | list of str, optional
        Source file(s) from which the destination file is created.
    dest_file : str, optional
        Destination/ target file which maybe needs to be computed and
        saved.
    force_save : bool, optional
        If True, forces a (re-)save. Default: False.
    check_age : bool, optional
        Check if source_files are younger than dest_file. If so,
        re-save. Default: False.

    """

    if force_save:
        return True

    # not yet computed
    if _any_file_does_not_exist(dest_file):
        return True

    # check if source file is newer as dest_file
    if check_age:
        return _source_files_newer_(source_files, dest_file)

    return False


def _check_all_files_exist(fnames):
    """
    error if one file does not exist
    """

    if _any_file_does_not_exist(fnames):
        msg = "file(s) missing:\n" + "\n".join(fnames)
        raise RuntimeError(msg)


def _any_file_does_not_exist(fnames):
    """
    check if any file in the list does not exist
    """

    fnames = _str2lst(fnames)

    inexistent = [not _os.path.isfile(fN) for fN in fnames]

    return np.any(np.array(inexistent))


def _source_files_newer_(source_files, dest_file):
    """
    check if the any of the source files is older than the dest file
    """

    source_files = _str2lst(source_files)

    # get timestamp of all files
    age_source = [_os.path.getctime(sf) for sf in source_files]
    age_dest = _os.path.getctime(dest_file)

    # compare timestamps
    source_is_older = np.array(age_source) < np.array(age_dest)

    # return true if any is older
    return np.all(source_is_older)


def _str2lst(list_or_string):
    """
    convert a string to a list
    """

    if isinstance(list_or_string, str):
        list_or_string = [list_or_string]

    return list_or_string
