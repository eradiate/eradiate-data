from pathlib import Path

import click
import numpy as np
import xarray as xr
from rich.console import Console
from ruamel.yaml import YAML
from rich.table import Table, Column

console = Console()


@click.group()
def cli():
    """
    Read and write CKD bin set definitions.
    """
    console.rule("[bold]Eradiate CKD Bin Set utility")


@cli.command()
@click.option(
    "-d",
    "--definition-file",
    default="definitions.yml",
    help="Path to definition file. Default: 'definitions.yml'.",
)
@click.option(
    "-n",
    "--dry-run",
    is_flag=True,
    help="Run in dry mode, i.e. do not write generation bin sets to NetCDF files.",
)
def make(definition_file, dry_run):
    """
    Write bin set definitions to MetCDF files.
    """
    # Load YAML
    definition_file = Path(definition_file).absolute()
    console.log(f"Loading definition file '{definition_file}'")
    yaml = YAML()
    with open(definition_file) as f:
        definitions = yaml.load(f)

    summarize(definitions)
    write(definitions, dry_run=dry_run)


def summarize(definitions):
    """
    Display a summary of bin set definitions.
    """
    table = Table(
        "ID",
        "Description",
        "Quad. type",
        Column("Quad. nodes", justify="right"),
        Column("wmin \[nm]", justify="right"),
        Column("wmax \[nm]", justify="right"),
        Column("wres \[nm]", justify="right"),
        title="Bin set definitions",
    )

    for bin_set_id in sorted(definitions.keys()):
        params = definitions[bin_set_id]

        row_items = [bin_set_id]
        row_items.append(params.get("description", "—"))

        row_items.extend(
            [
                f"{params[x]}"
                for x in ["quadrature_type", "quadrature_n", "wmin", "wmax", "wres"]
            ]
        )

        table.add_row(*row_items)

    console.print()
    console.print(table)
    console.print()


def write(definitions, dry_run=True):
    """
    Convert bin set definitions to NetCDF data files.
    """

    for bin_set_id, bin_set_params in definitions.items():
        quadrature_type = bin_set_params["quadrature_type"]
        quadrature_n = bin_set_params["quadrature_n"]

        wmin = bin_set_params["wmin"]
        wmax = bin_set_params["wmax"]
        wres = bin_set_params["wres"]

        # Generate bin data
        bin_wmins = np.arange(wmin, wmax, wres)
        bin_wmaxs = bin_wmins + wres
        bin_ids = [f"{x:g}" for x in 0.5 * (bin_wmins + bin_wmaxs)]

        # Store as dataset
        attrs = {"id": bin_set_id}
        if "description" in bin_set_params:
            attrs["description"] = bin_set_params["description"]
        attrs["quadrature_type"] = quadrature_type
        attrs["quadrature_n"] = quadrature_n

        ds = xr.Dataset(
            data_vars={
                "wmin": ("bin", bin_wmins, {"units": "nm"}),
                "wmax": ("bin", bin_wmaxs, {"units": "nm"}),
            },
            coords={"bin": bin_ids},
            attrs=attrs,
        )


        # Save as NetCDF
        out = Path(f"{bin_set_id}.nc").absolute()
        if dry_run:
            console.log(f"Would save to {out}")
        else:
            console.log(f"Saving to {out}")
            ds.to_netcdf(out)


@cli.command()
@click.argument("filename")
def show(filename):
    """
    Display NetCDF file contents.
    """
    filename = Path(filename).absolute()
    console.log(f"Opening {filename}")
    ds = xr.open_dataset(filename)
    console.print()
    console.print(ds)


if __name__ == "__main__":
    cli()
