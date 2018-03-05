# cesm - list simulation files and retrieve data

## Version
0.1.0

Version freeze for reproducibility.



## Usage

Define one or more simulations in `~/cesm_cases.yaml`:

```yaml
SMX2000:
    folder: /net/exo/landclim/mathause/cesm_data/
    name: f.e121.FC5.f19_g16.SMM2010_2000-io384.001
``` 


List / select files:
```ipython

import cesm

case = cesm.case('SMX2000')
case.lnd.h0.filename

Out[11]: 
['f.e121.FC5.f19_g16.SMM2010_2000-io384.001.clm2.h0.0001-01.nc',
 'f.e121.FC5.f19_g16.SMM2010_2000-io384.001.clm2.h0.0001-02.nc',
 'f.e121.FC5.f19_g16.SMM2010_2000-io384.001.clm2.h0.0001-03.nc'
 ...]

case.lnd.h1.sel(year=50)
Out[13]: '/net/cfc/landclim1/mathause/data/cesm121_russia10/f.e121.FC5.f19_g16.SMM2010_2000-io384.001/lnd/hist/f.e121.FC5.f19_g16.SMM2010_2000-io384.001.clm2.h1.0050-01-01-00000.nc'

``` 

Load data:
```ipython
cesm.load.var(case.atm.h0, 'TREFHT', year=50)
1 years require saving

Out[11]:
writing variable: 50 in 50..50
``` 


## Note

Currently this package is interwoven with my modifications to the `xarray`.
This has to be resolved.



