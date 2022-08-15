# Changelog

## 0.2.0 (unreleased)

- Code linting with `isort`, `black`, and `flake8`.
- Code modernization with `pyupgrade`.
- Remove some interdependencies with modified xarray.
- Remove the rest of the interdependencies with my modified version of xarray by "vendoring" them into `xarray_utils`. This package should now be usable in a standalone version. (But if this is a good idea is another question.)

## 0.1.1 (05 Mar 2018)

 - Inculdes `__version__`.
 - No other changes to the code.

## 0.1.0 (23 Feb 2018)

- Version freeze for reproducibility
- add ``get_cesm`` and ``get_cesm_data`` as template
