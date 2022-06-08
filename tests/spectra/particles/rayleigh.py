# %%

import datetime

utcnow = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

import xarray as xr
import numpy as np

import eradiate
from eradiate import unit_registry as ureg
from eradiate.units import symbol
eradiate.set_mode("mono")
%load_ext eradiate

# %%

def rayleigh_radprops() -> xr.Dataset:
    """
    Radiative properties of a Rayleigh scattering medium in [280, 2400] nm.

    The Rayleigh scattering phase function is computed from the analytical
    formula and tabulated on a regular scattering angle cosine grid.
    The Rayleigh scattering phase function does not depend on wavelength.

    The Rayleigh scattering coefficient is computed with
    :meth:`~eradiate.radprops.rayleigh.compute_sigma_s_air` with default
    the number density, i.e., standard air number density.

    The single-scattering albedo is set to 1.
    """
    w = np.arange(279.0, 2402.0) * ureg.nm

    albedo = np.ones_like(w) * ureg.dimensionless
    sigma_s = eradiate.radprops.rayleigh.compute_sigma_s_air(wavelength=w)
    sigma_t = (
        np.divide(
            sigma_s.m,
            albedo.m,
            where=albedo.m != 0,
            out=sigma_s.m,
        )
        * sigma_s.units
    )

    # Phase function
    # Note: rayleigh phase function does not change with wavelength
    mu = np.linspace(-1.0, 1.0, 201)
    arrays = [3.0 * (1 + np.square(mu)) / (16 * np.pi) / ureg.steradian for _ in w]
    phase = np.stack(arrays, axis=0).reshape(w.size, mu.size, 1, 1)

    return xr.Dataset(
        data_vars={
            "sigma_t": (
                "w",
                sigma_t.m,
                {
                    "standard_name": "air_volume_extinction_coefficient",
                    "long_name": "extinction coefficient",
                    "units": symbol(sigma_t.units),
                },
            ),
            "albedo": (
                "w",
                albedo.m,
                {
                    "standard_name": "single_scattering_albedo",
                    "long_name": "albedo",
                    "units": symbol(albedo.units),
                },
            ),
            "phase": (
                ("w", "mu", "i", "j"),
                phase.m,
                {
                    "standard_name": "scattering_phase_matrix",
                    "long_name": "phase matrix",
                    "units": symbol(phase.units),
                },
            ),
        },
        coords={
            "w": (
                "w",
                w.magnitude,
                {
                    "standard_name": "radiation_wavelength",
                    "long_name": "wavelength",
                    "units": symbol(w.units),
                },
            ),
            "mu": (
                "mu",
                mu,
                {
                    "standard_name": "scattering_angle_cosine",
                    "long_name": "scattering angle cosine",
                    "units": "dimensionless",
                },
            ),
            "i": ("i", [0]),
            "j": ("j", [0]),
        },
        attrs={
            "Conventions": "CF-1.9",
            "title": "Particle radiative properties",
            "history": f"{utcnow} - data set creation",
        }
    )
# %%

ds = rayleigh_radprops()



# %%

ds.to_netcdf("rayleigh.nc")
# %%
