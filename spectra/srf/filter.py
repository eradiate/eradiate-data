"""Eradiate spectral response function filtering utility"""

import datetime
import pathlib
import subprocess
import typing as t
import warnings

import click
import matplotlib.pyplot as plt
import numpy as np
import pint
import xarray as xr
from rich.console import Console
from rich.traceback import install

install(show_locals=False)

ureg = pint.UnitRegistry()
pint.set_application_registry(ureg)

console = Console()


def git_tag():
    return str(
        subprocess.check_output(
            [
                "git",
                "describe",
                "--abbrev=0",
            ],
            stderr=subprocess.STDOUT,
        )
    ).strip("'b\\n")


def update_attrs(srf: xr.Dataset, filter_name: str, filter_attr: str) -> None:
    """
    Update data set metadata to indicate that a filtering operation occurred.

    Parameters
    ----------
    srf: dataset
        Data set whose metadata to update.

    filter_name:
        Filter name.

    filter_attr:
        Content of the 'filter' attribute.
    """
    # filter attribute
    _value = srf.attrs.get("filter")
    previous_filter = _value + "\n" if _value is not None else ""

    # history attribute
    previous_history = srf.attrs["history"] + "\n"
    utcnow = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    author = f"eradiate-data ({git_tag()}) python spectra/srf/filter.py"
    history_attr = f"{utcnow} - data set filtering ({filter_name}) - {author}"

    # update attributes
    srf.attrs.update(
        {
            "history": f"{previous_history}{history_attr}",
            "filter": f"{previous_filter}{filter_attr}",
        }
    )


def _filtering_statistics(
    srf: xr.Dataset, filtered: xr.Dataset
) -> t.Mapping[str, t.Any]:
    """
    Compute filtering statistics.
    """
    ni = srf.w.size
    nf = filtered.w.size
    w_min_i = float(srf.w.values.min())
    w_max_i = float(srf.w.values.max())
    w_min_f = float(filtered.w.values.min())
    w_max_f = float(filtered.w.values.max())
    w_units = srf.w.attrs["units"]

    return {
        "initial": ni,
        "final": nf,
        "filtered": ni - nf,
        "filtered_perc": round(100.0 * (ni - nf) / ni, 2),
        "range_initial": f"[{w_min_i}, {w_max_i}] {w_units}",
        "range_final": f"[{w_min_f}, {w_max_f}] {w_units}",
    }


def _stat_report(stat: t.Mapping[str, str]) -> str:
    return (
        f"Filtered out {stat['filtered_perc']} % of data points "
        f"({stat['filtered']} points).\n"
        f"Initial range: {stat['range_initial']} "
        f"({stat['initial']} points).\n"
        f"Final range: {stat['range_final']} "
        f"({stat['final']} points)."
    )


def trim(ds: xr.Dataset) -> xr.Dataset:
    """
    Trim all leading zeros except last and all trailing zeros except first.

    Parameters
    ----------
    ds: dataset
        Data set to trim.

    Returns
    -------
    dataset
        Trimmed data set.
    """
    # trim
    wsize = ds.srf.values.size
    fsize = np.trim_zeros(ds.srf.values, trim="f").size
    bsize = np.trim_zeros(ds.srf.values, trim="b").size
    istart = wsize - fsize - 1 if wsize > fsize else 0
    istop = bsize if bsize < wsize else wsize - 1
    trimmed = ds.isel(w=range(istart, istop + 1))

    # update history attribute
    previous_history = ds.attrs["history"] + "\n"
    utcnow = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    author = f"eradiate-data ({git_tag()}) python spectra/srf/filter.py"
    history_attr = f"{utcnow} - trimmed data set - {author}"
    trimmed.attrs.update({"history": f"{previous_history}{history_attr}"})

    return trimmed


def _to_quantity(
    value: t.Union[None, str], default_units: str = "nm"
) -> t.Optional[pint.Quantity]:
    if value is None:
        return None
    else:
        # try to parse value into wavelength quantity
        parsed = ureg(value)
        if isinstance(parsed, pint.Quantity):
            return parsed
        else:  # float
            return ureg.Quantity(parsed, default_units)


def spectral_filter(
    srf: xr.Dataset,
    wmin: t.Optional[pint.Quantity] = None,
    wmax: t.Optional[pint.Quantity] = None,
    verbose: bool = True,
) -> xr.Dataset:
    """
    Drop points falling out of wavelength range specified by ``wmin`` and ``wmax``.
    """
    # filter
    w_units = srf.w.attrs["units"]

    if wmin is not None:
        _wmin = wmin.m_as(w_units)
        filtered = srf.where(srf.w >= _wmin, drop=True)
    else:
        filtered = srf
        _wmin = 0

    if wmax is not None:
        _wmax = wmax.m_as(w_units)
        filtered = filtered.where(srf.w <= _wmax, drop=True)
    else:
        _wmax = "inf"

    filter_attr = (
        f"All points in the original data set that fell out of the wavelength "
        f"range [{_wmin}, {_wmax}] {w_units} were dropped."
    )
    update_attrs(
        srf=filtered,
        filter_name="spectral filter",
        filter_attr=filter_attr,
    )

    # check filtering statistics
    stat = _filtering_statistics(srf=srf, filtered=filtered)
    if stat["final"] == 0:
        raise ValueError(
            f"Filtering this data set with wmin = {wmin} and wmax = {wmax} "
            f"would result in empty data set."
        )
    if verbose:
        print(_stat_report(stat=stat))

    return filtered


def _validate_threshold(value: float) -> None:
    if value < 0.0 or value >= 1.0:
        raise click.BadParameter(f"threshold value should be in [0, 1[ (got {value}).")


def threshold_filter(
    srf: xr.Dataset, value: float = 1e-3, verbose: bool = True
) -> xr.Dataset:
    """
    Drop data points where response is smaller or equal than a threshold value.
    """
    # validate input
    _validate_threshold(value=value)

    # check that filtering does not disconnect the wavelength space
    filter_indices = np.where(srf.srf.values > value)[0]
    consecutive = np.arange(filter_indices[0], filter_indices[0] + filter_indices.size)
    if not np.all(filter_indices == consecutive):
        warnings.warn(
            f"Filtering this data set with threshold value of {value} would "
            "disconnect the wavelength space. You probably do not want that."
        )

    # filter
    filtered = srf.where(srf.srf > value, drop=True)
    filter_attr = (
        f"All points in the original data set where the spectral response "
        f"function evaluated to {value} or smaller were dropped."
    )
    update_attrs(
        srf=filtered,
        filter_name="threshold filter",
        filter_attr=filter_attr,
    )

    # check filtering statistics
    stat = _filtering_statistics(srf=srf, filtered=filtered)
    if stat["final"] == 0:
        raise ValueError(
            f"Filtering this data set with threshold value of {value} would "
            f"result in empty data set."
        )
    if verbose:
        print(_stat_report(stat=stat))

    return filtered


def _validate_percentage(value: float) -> None:
    if value < 0.0 or value > 100.0:
        raise ValueError(f"value must be within [0, 100.0] (got {value})")


def cumsum_filter_w_bounds(ds: xr.Dataset, percentage: float = 99.0):
    """
    Find the wavelength bounds for the cumsum filter.

    Parameters
    ----------
    ds: dataset
        Dataset to filter.

    percentage: float
        Keep data that contribute to this percentage of the integrated spectral
        response.

    Returns
    -------
    tuple
        Wavelength bounds.
    """
    _validate_percentage(value=percentage)

    dwmin = ds.w.diff(dim="w").values.min()
    wmin = ds.w.values.min()
    wmax = ds.w.values.max()
    wnum = int((wmax - wmin) / dwmin) + 1
    wreg = np.linspace(wmin, wmax, wnum)
    srfreg = ds.srf.interp(w=wreg)
    cumsum = np.cumsum(srfreg)
    cumcum_max = cumsum.values.max()
    dx = (1 - (percentage / 100)) / 2

    w_left = cumsum.where(cumsum < dx * cumcum_max, drop=True).w.values
    if w_left.size > 0:
        w0 = w_left[-1]
    else:
        w0 = wmin

    w_right = cumsum.where(cumsum > (1 - dx) * cumcum_max, drop=True).w.values
    if w_right.size > 0:
        w1 = w_right[0]
    else:
        w1 = wmax

    return w0, w1


def cumsum_filter(srf: xr.Dataset, percentage: float = 99.0, verbose: bool = True):
    """
    Keep only data that contribute to the integrated spectral response value
    to the amount of the specified percentage.

    Parameters
    ----------
    ds: dataset
        Dataset to filter.

    percentage: float
        Keep data that contribute to this percentage of the integrated spectral
        response.

    Returns
    -------
    tuple
        Wavelength bounds.
    """
    w_bounds = cumsum_filter_w_bounds(ds=srf, percentage=percentage)
    filtered = srf.where(srf.w >= w_bounds[0], drop=True).where(
        srf.w <= w_bounds[1], drop=True
    )
    filter_attr = (
        f"Data points that did not contribute to {percentage} % of the "
        f"integrated spectral reponse were dropped."
    )
    update_attrs(
        srf=filtered,
        filter_name="cumsum filter",
        filter_attr=filter_attr,
    )

    # check filtering statistics
    stat = _filtering_statistics(srf=srf, filtered=filtered)
    if stat["final"] == 0:
        raise ValueError(
            f"Filtering this data set with {percentage=} "
            f"would result in empty data set."
        )
    if verbose:
        print(_stat_report(stat=stat))

    return filtered


@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
)
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="Do not write filtered data to file.",
)
@click.option(
    "-t",
    "--threshold",
    default=None,
    show_default=True,
    type=float,
    help="Data points where response is less then or equal to this value are dropped.",
)
@click.option(
    "-w",
    "--wmin",
    default=None,
    show_default=True,
    help="Lower wavelength value",
)
@click.option(
    "-W",
    "--wmax",
    default=None,
    show_default=True,
    help="Upper wavelength value",
)
@click.option(
    "-p",
    "--percentage",
    default=None,
    show_default=True,
    type=float,
    help="Data points that do not contribute to this percentage of the integrated spectral response are dropped",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=False,
)
def apply_filter(
    filename: str,
    output: str,
    verbose: bool = False,
    dry_run: bool = False,
    threshold: t.Optional[float] = None,
    wmin: t.Optional[t.Union[float, str]] = None,
    wmax: t.Optional[t.Union[float, str]] = None,
    percentage: t.Optional[float] = None,
    interactive: bool = False,
):
    """
    Spectral response function filtering utility.

    FILENAME specifies the path to the spectral response function data to filter.
    OUTPUT specified the path where to write the filtered data.
    """
    console.rule("[bold]Eradiate spectral response function filtering utility")

    input_path = pathlib.Path(filename).absolute()
    console.log(f"Loading {input_path}")

    with xr.load_dataset(input_path) as srf:

        console.log(f"Trimming data set...")
        filtered = trim(ds=srf)

        # cumsum filter
        if percentage is not None:
            filtered = cumsum_filter(
                srf=filtered,
                percentage=percentage,
                verbose=verbose,
            )

        # spectral filter
        if wmin is not None or wmax is not None:
            _wmin = _to_quantity(value=wmin)
            _wmax = _to_quantity(value=wmax)
            filtered = spectral_filter(
                srf=filtered,
                wmin=_wmin,
                wmax=_wmax,
                verbose=verbose,
            )

        # threshold filter
        if threshold is not None:
            filtered = threshold_filter(
                srf=filtered,
                value=threshold,
                verbose=verbose,
            )

    if interactive:
        # srf plot pops up
        show(
            ds=srf,
            title=filename,
            threshold=threshold,
            wmin=wmin,
            wmax=wmax,
            percentage=percentage,
        )

        if click.confirm("Are you sure you want to apply this filter?", abort=True):
            write_filtered_data(output=output, filtered=filtered, dry_run=dry_run)

    else:
        write_filtered_data(output=output, filtered=filtered, dry_run=dry_run)

    console.log("Done!")


def write_filtered_data(output, filtered, dry_run: bool = False) -> None:
    """Write filtered data to disk."""
    output_path = pathlib.Path(output).absolute()
    if dry_run:
        console.log(f"Would write filtered data to {output_path}")
    else:
        console.log(f"Writing filtered data to {output_path}")
        filtered.to_netcdf(output)


def show(
    ds: xr.Dataset,
    title: str,
    threshold: t.Optional[float] = None,
    wmin: t.Optional[pint.Quantity] = None,
    wmax: t.Optional[pint.Quantity] = None,
    percentage: t.Optional[float] = None,
):
    """
    Show filtered region on spectral response function plot.

    FILENAME specifies the path to the spectral response function data to filter.
    OUTPUT specified the path where to save the visualisation.
    """
    plt.figure(dpi=100)
    ax = plt.gca()

    plt_params = {
        "lw": 0.6,
        "marker": ".",
        "markersize": 2,
        "yscale": "log",
    }
    trimmed = trim(ds=ds)
    trimmed.srf.plot(**plt_params)

    if threshold is not None:
        _validate_threshold(value=threshold)
        plt.axhline(y=threshold, color="red", lw=0.5)
        # keep region
        ax.fill_between(
            trimmed.w.values,
            0,
            trimmed.srf.values,
            where=trimmed.srf.values > threshold,
            facecolor="green",
            alpha=0.1,
        )
        plt.axhline(y=threshold, color="red", lw=0.5)
        # drop region
        ax.fill_between(
            trimmed.w.values,
            0,
            trimmed.srf.values,
            where=trimmed.srf.values <= threshold,
            facecolor="red",
            alpha=0.1,
        )

    if wmin is not None or wmax is not None:
        _wmin = _to_quantity(value=wmin)
        _wmax = _to_quantity(value=wmax)

        if _wmin is not None:
            _wmin_value = _wmin.m_as(ds.w.attrs["units"])
            plt.axvline(x=_wmin_value, color="red", lw=0.5)
            # drop region
            ax.fill_between(
                trimmed.w.values,
                0,
                trimmed.srf.values,
                where=trimmed.w.values < _wmin_value,
                facecolor="red",
                alpha=0.1,
            )
        else:
            _wmin_value = 0.0

        if _wmax is not None:
            _wmax_value = _wmax.m_as(ds.w.attrs["units"])
            plt.axvline(x=_wmax_value, color="red", lw=0.5)
            # drop region
            ax.fill_between(
                trimmed.w.values,
                0,
                trimmed.srf.values,
                where=trimmed.w.values > _wmax_value,
                facecolor="red",
                alpha=0.1,
            )
        else:
            _wmax_value = np.inf

        # keep region
        ax.fill_between(
            trimmed.w.values,
            0,
            trimmed.srf.values,
            where=(
                (trimmed.w.values >= _wmin_value) & (trimmed.w.values <= _wmax_value)
            ),
            facecolor="green",
            alpha=0.1,
        )

    if percentage is not None:
        wmin, wmax = cumsum_filter_w_bounds(ds=ds, percentage=percentage)
        # drop regions
        plt.axvline(x=wmin, color="red", lw=0.5)
        ax.fill_between(
            trimmed.w.values,
            0,
            trimmed.srf.values,
            where=trimmed.w.values < wmin,
            facecolor="red",
            alpha=0.1,
        )
        plt.axvline(x=wmax, color="red", lw=0.5)
        ax.fill_between(
            trimmed.w.values,
            0,
            trimmed.srf.values,
            where=trimmed.w.values > wmax,
            facecolor="red",
            alpha=0.1,
        )
        # keep region
        ax.fill_between(
            trimmed.w.values,
            0,
            trimmed.srf.values,
            where=((trimmed.w.values >= wmin) & (trimmed.w.values <= wmax)),
            facecolor="green",
            alpha=0.1,
        )

    plt.title(title)
    plt.tight_layout()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    apply_filter()
