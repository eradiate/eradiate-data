# Spectral response function data sets

## Structure

Spectral response function data sets are stored as NetCDF data sets, whose
structure is the following:

**Coordinates (\* means also dimension)**

* `*w` (float): wavelength `[length]`

**Variables**

* `srf [w]` (float): spectral response function `[dimensionless]`
* `srf_u [w]` (float): spectral response function uncertainty `[dimensionless]`

**Metadata**

* `platform` (str): platform name, e.g. `"Sentinel-2A"`
* `instrument` (str): instrument name, e.g. `"SLSTR"`
* `band` (str): band identifier, e.g. `"1"`

As per the [CF Conventions](https://cfconventions.org/), if possible and/or
relevant, the following data set attributes should be provided:

* `title` (str)
* `institution` (str)
* `source` (str)
* `history` (str)
* `reference` (str)
* `comment` (str)

and the attribute `Conventions` should be set (e.g., `"CF-1.10"`).

## Raw versus prepared data sets

All spectral response function datasets are made available in a so-called _raw_
version, where the data matches that from the data provider, except that the
irrelevant trailing and leading zeros have been removed in a trimming process.

Additionally, some dataset are made available in a so-called _prepared_ version,
where the datasets have been further filtered to yield a better
**simulation speed versus accuracy tradeoff**.
The filtering parameters are stored in `prepared.json`.

Refer to the Eradiate documentation for more information about spectral response
function trimming and filtering.


## File naming convention

* Raw spectral response function data sets are named
`<platform>-<instrument>-<band>-raw.nc`, e.g. `sentinel_2a-slstr-1-raw.nc`.
* Prepared spectral response function data sets are named
`<platform>-<instrument>-<band>.nc`, e.g. `sentinel_2a-slstr-1.nc`.
