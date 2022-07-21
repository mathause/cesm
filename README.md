# cesm - list simulation files and retrieve data

## Usage

Define one or more simulations in `~/cesm_cases.yaml`:

```yaml
SMX2000:
    folder: /net/exo/landclim/mathause/cesm_data/
    name: f.e121.FC5.f19_g16.SMM2010_2000-io384.001
``` 


List / select files:

```python
import cesm

case = cesm.case('SMX2000')
print(case.lnd.h0.filename)

print(case.lnd.h1.sel(year=50))
```

Output
```
['f.e121.FC5.f19_g16.SMM2010_2000-io384.001.clm2.h0.0001-01.nc',
 'f.e121.FC5.f19_g16.SMM2010_2000-io384.001.clm2.h0.0001-02.nc',
 'f.e121.FC5.f19_g16.SMM2010_2000-io384.001.clm2.h0.0001-03.nc'
 ...]

'/net/.../f.e121.FC5.f19_g16.SMM2010_2000-io384.001.clm2.h1.0050-01-01-00000.nc'
``` 

Load data:
```python
TREFHT = cesm.load.var(case.atm.h0, 'TREFHT', year=50)
print(TREFHT)
```

Output
```
1 years require saving
writing variable: 50 in 50..50

<xarray.Dataset>
Dimensions:  (lat: 96, lon: 144, time: 12)
Coordinates:
  * lat      (lat) float64 -90.0 -88.11 -86.21 -84.32 -82.42 -80.53 -78.63 ...
  * lon      (lon) float64 0.0 2.5 5.0 7.5 10.0 12.5 15.0 17.5 20.0 22.5 ...
  * time     (time) datetime64[ns] 2000-01-16T12:00:00 2000-02-15 ...
Data variables:
    TREFHT   (time, lat, lon) float32 242.634 243.037 242.642 242.609 ...

``` 


## Note

Currently this package is interwoven with my modifications to the `xarray`.
This has to be resolved.



