import numpy as np
from numpy import pi, square
from datetime import datetime
import xarray as xr


def lorentzian_pdf(x, x0=0., gamma=1.):
    """Computes the Lorentz probability density function.
    """
    return (1 / (pi * gamma)) * square(gamma) / (square(x-x0) + square(gamma))

def make_dataset():
    """This function generates a test absorption cross section data set which
    can then be used to extract absorption cross section and compute the
    monochromatic absorption coefficient.

    The data set includes one absorbing species and can be interpolated in
    pressure and wavenumber values.
    """

    # pressure values
    n_p = 8
    p = np.geomspace(1e3, 1e5, num=n_p)  # [Pa]

    # wavenumber values
    n_wv = 10001
    wv = np.linspace(18000., 18010., num=n_wv)  # [cm^-1]

    # pressure dependence of line width and line position
    gamma_ref = 1e-5
    p_ref = 1e2
    gamma = (p-p_ref) * gamma_ref
    x0 = 18005. + (p-p_ref) * 1e-5

    # absorption cross section data
    intensity = 1e-25  # [cm^3]
    data = np.zeros((1, n_p, n_wv))
    for i, pressure in enumerate(p):
        data[0, i] = lorentzian_pdf(wv, x0=x0[i], gamma=gamma[i])

    function_name = "eradiate-data/tests/datasets/absorption_cross_section/make_dataset.py"

    # create data set
    return xr.DataArray(
        data=data,
        dims=("species", "pressure", "wavenumber"),
        coords={
            "pressure": ("pressure", p, {"standard_name": "air_pressure", "units": "Pa"}),
            "wavenumber": ("wavenumber", wv, {"standard_name": "wavenumber", "units": "cm^-1"}),
            "species": ("species", np.array(["test_mixture"]), {"standard_name": "species", "units": ""})
        },
        name="absorption_cross_section",
        attrs={
            "standard_name": "absorption_cross_section",
            "units": "cm^2",
            "convention": "CF-1.8",
            "title": "Test absorption cross section data set",
            "history": (
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - absorption cross section data set creation - {function_name}"
            ),
            "source": function_name,
            "references": ""
        }
    )

# Write to hard drive
ds = make_dataset()
ds.to_netcdf("test_dataset.nc")
