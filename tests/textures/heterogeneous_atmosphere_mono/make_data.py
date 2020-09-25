from copy import copy

import numpy as np
import xarray as xr

from eradiate.scenes.atmosphere.heterogeneous import _write_binary_grid3d


def make_data():
    """This function generates a test data set which can then be used to create
    test gridded data files.
    """
    # Coordinates
    z = np.linspace(0, 1, 11)

    channels = 3
    lambda_min = 380.
    lambda_max = 830.
    lambdas = np.linspace(lambda_min, lambda_max, channels)
    d_lambda = lambda_max - lambda_min
    n_lambdas = (lambdas - lambda_min) / d_lambda

    # Create dataset
    def empty():
        return np.empty((1, 1, len(z), len(lambdas)))

    ds = xr.Dataset(
        data_vars={
            "density": (["x", "y", "z", "wavelength"], empty()),
            "sigma_t": (["x", "y", "z", "wavelength"], empty()),
            "sigma_a": (["x", "y", "z", "wavelength"], empty()),
            "sigma_s": (["x", "y", "z", "wavelength"], empty()),
            "albedo": (["x", "y", "z", "wavelength"], empty()),
        },
        coords={
            "x": [0],
            "y": [0],
            "z": copy(z),
            "wavelength": copy(lambdas)
        }
    )

    # Populate variables
    for z in ds["z"]:
        ds["albedo"].loc[dict(x=0, y=0, z=z)] = 0.5 * (1 - n_lambdas ** 4) + 0.5

    for wavelength in ds["wavelength"]:
        ds["density"].loc[dict(x=0, y=0, wavelength=wavelength)] = np.exp(-ds.z * 3.)

    ds["sigma_t"] = ds["density"] * 2.
    ds["sigma_s"] = ds["sigma_t"] * ds["albedo"]
    ds["sigma_a"] = ds["sigma_t"] - ds["sigma_s"]

    return ds


# Write to hard drive
ds = make_data().interp(wavelength=550.)
filenames = {}

for varname in ["sigma_t", "sigma_a", "sigma_s", "albedo"]:
    filename = f"{varname}.vol"
    filenames[varname] = filename
    data = ds[varname]
    _write_binary_grid3d(filename, data)
