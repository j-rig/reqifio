#!/usr/bin/env python3
"""
cli.py

A command-line interface using Click to convert a ReqIF file into CSV files and/or a SQLite database.
It reads a ReqIF file using reqifio.reqif_parser, writes CSV files using reqifio.csv_adapter,
and writes to a SQLite database using reqifio.sqlite_adapter.
"""

import click
from reqifio import reqif_parser, csv_adapter, sqlite_adapter


@click.command()
@click.argument("reqif_file", type=click.Path(exists=True))
@click.option(
    "--csv-folder",
    type=click.Path(file_okay=False),
    help="Output folder where CSV files will be written.",
)
@click.option("--sqlite-file", type=click.Path(), help="Output SQLite database file.")
def main(reqif_file, csv_folder, sqlite_file):
    """
    Converts a ReqIF file into CSV files and/or a SQLite database.

    REQIF_FILE is the path to the input ReqIF XML file.

    Use --csv-folder to specify an output folder for CSV files and/or
    --sqlite-file to specify an output SQLite database file.
    """
    click.echo(f"Parsing ReqIF file: {reqif_file}")
    document = reqif_parser.parse_reqif_file(reqif_file)

    if csv_folder:
        click.echo(f"Writing CSV files to folder: {csv_folder}")
        csv_adapter.write_doc_to_csv(document, csv_folder)
        click.echo("CSV conversion completed.")

    if sqlite_file:
        click.echo(f"Writing to SQLite database file: {sqlite_file}")
        sqlite_adapter.write_doc_to_db(document, sqlite_file)
        click.echo("SQLite database conversion completed.")

    if not csv_folder and not sqlite_file:
        click.echo(
            "No output option provided. Please specify either --csv-folder or --sqlite-file."
        )


if __name__ == "__main__":
    main()
