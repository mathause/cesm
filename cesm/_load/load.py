import six
import numpy as np
import os
import xarray as xr
import pandas as pd
from scipy import stats

def var(hist, varname, year):
    
    source_files = _postprocess(hist, varname, year=year,
                        force_save=False, check_age=False)

    
    return xr.read_netcdfs_cesm(source_files, 'time')

# -----------------------------------------------------------------------------


def clim_monthly(hist, varname, year):

    ds = var(hist, varname, year)
    
    return ds.groupby('time.month').mean(dim='time')

# -----------------------------------------------------------------------------


def soillev(hist, varname, year, transform_func=None):

    prefix = 'soillev'
    transform_func_internal = trans_soilliq_soillev

    fNs = _postprocess(hist, varname, year, prefix=prefix,
                       transform_func=transform_func_internal, new_var=None,
                       force_save=False, check_age=False)

    return xr.read_netcdfs_cesm(fNs, 'time', transform_func=transform_func)

# -----------------------------------------------------------------------------


def var_SREX_LAND(hist, varname, year, force_save=False, check_age=False):

    prefix = 'SREX'
    transform_func = trans_SREX_LAND_var

    fNs = _postprocess(hist, varname, year, prefix=prefix,
                       transform_func=transform_func, new_var=None,
                       force_save=force_save, check_age=check_age)

    return xr.read_netcdfs_cesm(fNs, 'time')

# -----------------------------------------------------------------------------


def annual_XXX(hist, varname, year, apply_func='mean'):

    prefix = ['annual', apply_func]
    
    transform_func = _trans_annual_XXX(apply_func)

    fNs = _postprocess(hist, varname, year, prefix=prefix,
                       transform_func=transform_func, new_var=None,
                       force_save=False, check_age=False)

    return xr.read_netcdfs_cesm(fNs, 'time')

# ======================================================================
# TRANSFORMATION FUNCTIONS
# ======================================================================

def trans_extract_var(varname, hist):
    # extract a named variable
    def _inner(ds):
        return ds[varname]
    return _inner


# -----------------------------------------------------------------------------

def trans_evapotranspiration(varname, hist):
    # evatranspiration is QSOIL + QVEGE + QVEGT
    def _inner(ds):
        return ds.QSOIL + ds.QVEGE + ds.QVEGT
    return _inner


# -----------------------------------------------------------------------------

def trans_soilliq(varname, hist):
    # we only need the first 10 levels of SOILLIQ/ SOILICE
    def _inner(ds):
        return ds[varname].isel(levgrnd=slice(None, 10))
    return _inner


# -----------------------------------------------------------------------------

def trans_SREX_LAND_var(varname, hist):

    # obtain necessary data
    import regionmask
    landfrac = hist.data.landfrac
    weight = hist.data.weight

    wgt = landfrac
    mask = regionmask.defined_regions.srex.mask(landfrac, wrap_lon=True)
    abbrevs = ['global_land'] + regionmask.defined_regions.srex.abbrevs

    # extract a named variable
    def _inner(ds):
        ds = ds[varname]
        
        # global land mean
        ave = [ds.average(dim=('lat', 'lon'), weights=wgt)]

        # srex mean
        for i in range(1, 27):
            a = ds.where(mask == i).average(dim=('lat', 'lon'), weights=wgt)

            ave.append(a)


        ds = xr.concat(ave, dim='srex')

        # add the name of the regions
        ds = ds.assign_coords(**{'srex_abbrev': ('srex', abbrevs)})

        return ds

    return _inner


# -----------------------------------------------------------------------------

def trans_soilliq_soillev(varname, hist):
    # split soil into three parts: 0 to 10 // 10 to 100 // 100 to 380 cm
    
    def _inner(ds):

        # only the 10 first levels
        ds = ds[varname].isel(levgrnd=slice(None, 10))

        # split levgrnd
        soillev = pd.cut(ds.levgrnd, [0, 0.1, 1, 2.9])
        
        # add the new category 
        ds = ds.assign_coords(soillev=('levgrnd', soillev))
        
        # take sum over the three parts
        ds = ds.groupby('soillev').sum(dim='levgrnd', skipna=False)

        return ds

    return _inner


# -----------------------------------------------------------------------------

def _trans_annual_XXX(apply_func):

    def _trans_annual_XXX_internal(varname, hist):

        def _inner(ds):

            ds = ds[varname]
            year = stats.mode(ds['time.year'].values)[0][0]
            ds = ds.sel(time=str(year))
            ds = ds.resample('A', 'time', how=apply_func, keep_attrs=True)

            return ds
        return _inner
    return _trans_annual_XXX_internal


# =============================================================================



def _postprocess(hist, varname, year, prefix='', transform_func=trans_extract_var,
                 new_var=None, force_save=False, check_age=False):

    prefix = _prefix(prefix, varname)

    if new_var is None:
        new_var = varname

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
        

    if years_require_saving:
        n_years_require_saving = len(years_require_saving)
        print(str(n_years_require_saving) + ' years require saving')


    # prepare for parallel processing
    for year in years_require_saving:

        print('writing variable: {} in {}..{}'.format(year, yearmin, yearmax))
        # name of source and destination files
        source_files = hist.sel(year=year)
        dest_file = _destfile_name(hist, prefix, year)

        # save it
        _save_var(source_files, dest_file, varname, hist, new_var,
                  transform_func)



    return dest_files


def _destfile_name(hist, prefix, year):
    return hist.post.pre_suf(prefix, str(year), prefix_folder=True)

def _prefix(prefix, varname):
    prefix = prefix if prefix != '' else []
    if isinstance(prefix, basestring):
        prefix = [prefix]
        
    return [varname] + prefix


def _save_var(source_files, dest_file, varname, hist, new_var,
              transform_func):

    """save variable in annual files, one per variable"""

    ds = xr.read_netcdfs_cesm(source_files, 'time', transform_func(varname, hist))

    ds = ds.to_dataset(name=new_var)

    ds.to_netcdf(dest_file, format='NETCDF4_CLASSIC')




def _maybe_save(source_file=None, dest_file=None,
                force_save=False, check_age=False):

    # force_save recompute
    if force_save:
        return True

    # not yet computed
    if _any_file_does_not_exist(dest_file):
        return True

    # check if source file is newer as dest_file
    if check_age:
        return _source_files_newer_(source_file, dest_file)

    return False


def _check_all_files_exist(fnames):
    # error if one file does not exist

    if _any_file_does_not_exist(fnames):
        msg = "file(s) missing:\n" + '\n'.join(fnames)
        raise RuntimeError(msg)




def _any_file_does_not_exist(fnames):
    """
    check if any file in the list does not exist
    """

    fnames = _str2lst(fnames)
    inexistent = [not os.path.isfile(fN) for fN in fnames]
    
    return np.any(np.array(inexistent))




def _source_files_newer_(source_files, dest_file):

    if isinstance(source_files, six.string_types):
        source_files = [source_files]

    age_source = [os.path.getctime(sf) for sf in source_files]
    age_dest = os.path.getctime(dest_file)

    source_is_older = np.array(age_source) < np.array(age_dest)

    return np.all(source_is_older)



def _str2lst(list_or_string):
    # convert a string to a list

    if isinstance(list_or_string, six.string_types):
        list_or_string = [list_or_string]    

    return list_or_string








