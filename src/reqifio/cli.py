#!/usr/bin/env python
"""
convert_reqif.py

This script uses Click to read a ReqIF file and output either a SQLite database or a collection of CSV files.
Usage examples:
    python convert_reqif.py input.reqif --mode sqlite --output reqif.db
    python convert_reqif.py input.reqif --mode csv --output ./csv_output
"""

import sys
import click
from .reqif_parser import ReqIFParser
from .sqlite_adapter import SQLiteAdapter
from .csv_adapter import CSVAdapter


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["sqlite", "csv"], case_sensitive=False),
    required=True,
    help='Output mode: "sqlite" or "csv".',
)
@click.option(
    "--output",
    "-o",
    type=str,
    required=True,
    help="Output target. For sqlite, provide a database file path; for csv, provide a folder path.",
)
def convert_reqif(input_file, mode, output):
    """
    Convert a ReqIF file (INPUT_FILE) to a SQLite database or CSV files based on MODE.
    """
    click.echo(f"Parsing ReqIF from {input_file} ...")
    parser = ReqIFParser(input_file)
    reqif_model = parser.parse()

    if mode.lower() == "sqlite":
        click.echo(f"Writing ReqIF model to SQLite DB: {output} ...")
        adapter = SQLiteAdapter(output)
        adapter.create_schema()
        adapter.write(reqif_model)
        click.echo("SQLite output created successfully.")
    elif mode.lower() == "csv":
        click.echo(f"Writing ReqIF model to CSV files in folder: {output} ...")
        adapter = CSVAdapter(output)
        adapter.write(reqif_model)
        click.echo("CSV output created successfully.")
    else:
        click.echo("Unsupported mode. Use 'sqlite' or 'csv'.")
        sys.exit(1)


def main():
    convert_reqif()


if __name__ == "__main__":
    convert_reqif()
