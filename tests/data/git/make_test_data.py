import xarray as xr

ds = xr.Dataset(
    coords={"x": range(10), "y": range(10)},
    data_vars={
        "some_var": (["x", "y"], [[i + j for i in range(10)] for j in range(10)])
    },
)
ds.to_netcdf("registered_dataset.nc")
ds.to_netcdf("unregistered_dataset.nc")
