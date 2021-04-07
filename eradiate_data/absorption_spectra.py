"""Absorption cross section spectrum data sets shipped with Eradiate.

**Category ID**: ``absorption_spectrum``

.. list-table:: Available data sets and corresponding identifiers
   :widths: 1 1 1
   :header-rows: 1

   * - Dataset ID
     - Reference
     - Spetral range [nm]
   * - ``spectra-us76_u86_4``
     - ``eradiate-datasets_maker/scripts/spectra/acs/spectra/us76_u86_4.py``
     - [~389, 2500]
"""

import numpy as np
import xarray as xr
import json

from .dvc_data_getter import DVCDataGetter
from eradiate_data import path_resolver as _presolver
#from .._units import unit_registry as ureg

_US76_U86_4_PATH = "spectra/absorption/us76_u86_4"
_US76_U86_4_PREF = "spectra-us76_u86_4"


class _AbsorptionGetter(DVCDataGetter):
    module_path=Path(os.path.abspath(os.path.dirname(__file__)))
    absorption_dataset_description = json.load(open(module_path / "spectra" / "absorption" / "us76_u86_4.json"))

    PATHS={
        **{folder: [f"spectra/absorption/us76_u86_4/{folder}/{file}" for file in absorption_dataset_description["files"]]
            for folder in absorption_dataset_description["folders"] if folder != "test"},
        "test": [f"tests/absorption/us76_u86_4/{file}" for file in absorption_dataset_description["files"]],
    }

    @classmethod
    def open(cls, id, download_missing=True):
        paths = cls.path(id)
        paths = [_presolver.resolve(path) for path in paths]

        try:
            return xr.open_mfdataset(paths)
        except OSError as e:
            if not download_missing:
                raise OSError(f"while opening file at {path}: {str(e)}")
            else:
                for path in paths:
                    cls.gather_file(path)
                cls.open(id, download_missing=False)

    @classmethod
    def find(cls):
        result = {}

        for id in cls.PATHS.keys():
            paths = _presolver.glob(cls.path(id))
            result[id] = bool(len(list(paths)))

        return result


#@ureg.wraps(ret=None, args=("cm^-1", None, None), strict=False)
def find_dataset(wavenumber, absorber="us76_u86_4", engine="spectra"):
    """Finds the dataset corresponding to a given wavenumber,
    absorber and absorption cross section engine.

    Parameter ``wavenumber`` (:class:`~pint.Quantity`):
        Wavenumber value [cm^-1].

    Parameter ``absorber`` (str):
        Absorber name.

    Parameter ``engine`` (str):
        Engine used to compute the absorption cross sections.

    Returns → str:
        Available dataset id.
    """
    if absorber == "us76_u86_4":
        if engine != "spectra":
            raise ValueError(f"engine {engine} is not supported.")
        for d in [_AbsorptionGetter.PATHS[k] for k in _AbsorptionGetter.PATHS
                  if k != "test"]:
            path = _presolver.resolve(d.strip("/*.nc"))
            if path.is_absolute():
                _engine, _absorber, w_range = tuple(path.name.split("-"))
                if _absorber == absorber and _engine == engine:
                    w_min, w_max = w_range.split("_")
                    if float(w_min) <= wavenumber < float(w_max):
                        return path.name
        raise ValueError(f"could not find the dataset corresponding to "
                         f"wavenumber = {wavenumber}, "
                         f"absorber = {absorber} and "
                         f"engine = {engine}")
    else:
        raise ValueError(f"absorber {absorber} is not supported.")
