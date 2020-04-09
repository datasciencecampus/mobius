#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os

import click
import pandas as pd
from google.cloud.storage.client import Client

import mobius

BUCKET = "mobility-reports"


def get(filetype="SVG", regex="\d{4}-\d{2}-\d{2}_.+"):
    client = Client.create_anonymous_client()
    blobs = filter(
        lambda b: re.match(f"{filetype}/{regex}", b.name),
        client.list_blobs(BUCKET),
    )
    return list(blobs)


def get_country(blob):
    name = blob.name.split("/")[-1]
    country = name.replace("Mobility_Report_en", "")[11:-5]
    return country


def show(filetype):
    url_prefix = "https://storage.cloud.google.com/mobility-reports/"
    country_names = pd.read_csv(os.path.join(os.getcwd(),'config/country_codes.csv'))
    MAXLEN = 25
    MAXLEN_COUNTRY = 40
    blobs = list(get(filetype=filetype))
    print("Available countries:")
    for i, blob in enumerate(blobs):
        country = get_country(blob)
        country_name = country_names.loc[country_names['code'] == f"-{country[0:2]}", 'name'].item()
        country = (
            country + (" " * (MAXLEN - len(country)))
            if len(country) < MAXLEN
            else country[:MAXLEN]
        )
        country_name = (
            country_name + (" " * (MAXLEN_COUNTRY - len(country_name)))
            if len(country_name) < MAXLEN_COUNTRY
            else country_name[:MAXLEN_COUNTRY]
        )


        iteration = str(i + 1)
        iteration = (
            iteration
            if (len(iteration) == 3)
            else (" " * (3 - len(iteration)) + iteration)
        )
        print(f" {iteration}. {country} {country_name} ({url_prefix + blob.name})")



@click.group(help="Downloader and processor for Google mobility reports")
def cli():
    pass


@cli.command(help="List all the PDFs available in the buckets")
def ls():
    show("SVG")


@cli.command(help="List all the SVGs available in the buckets")
def svg():
    show("SVG")


@cli.command(help="List all the PDFs available in the buckets")
def pdf():
    show("PDF")


@cli.command(help="Download pdf and svg for a given country using the country code")
@click.argument("COUNTRY_CODE")
def download(country_code):
    client = Client.create_anonymous_client()

    def _download(blobs, extension):

        if len(blobs):
            for blob in blobs:

                fname = f"{extension}s/{get_country(blob)}.{extension}"
                with open(fname, "wb+") as fileobj:

                    client.download_blob_to_file(blob, fileobj)

            print(
                f"Download {country_code} {extension} complete. Saved to /{extension}s"
            )
        else:
            print(f"Could not find a {extension} file for code {country_code}")

    regex = f"\d{{4}}-\d{{2}}-\d{{2}}_{country_code}_M.+"

    blobs = get(filetype="SVG", regex=regex)
    _download(blobs, "svg")

    blobs = get(filetype="PDF", regex=regex)
    _download(blobs, "pdf")


@cli.command(help="Process a given country SVG")
@click.argument("INPUT_LOCATION")
@click.argument("OUTPUT_FOLDER")
@click.argument("DATES_FILE", default=None)
@click.option(
    "-f", "--folder", help="If provided will overwrite the output folder name",
)
@click.option(
    "-s", "--svgs", help="Enables saving of svgs that get extracted", is_flag=True,
)
@click.option(
    "-p",
    "--plots",
    is_flag=True,
    help="Enables creation and saving of additional PNG plots",
)
def proc(input_location, output_folder, folder, dates_file, svgs, plots):

    date_lookup_df = mobius.io.read_dates_lookup(dates_file)

    print(f"Processing {input_location}")
    output_folder = mobius.io.prep_output_folder(input_location, output_folder, folder)
    data = mobius.graphs.graph_process(input_location, output_folder, svgs)

    mobius.csv.process_all(data, date_lookup_df, output_folder, plots, save=True)


@cli.command(help="Produce summary CSV of regional headline figures from CSV")
@click.argument("INPUT_PDF", type=click.Path(exists=True))
@click.argument("OUTPUT_FOLDER")
def summary(input_pdf, output_folder):

    with mobius.io.open_document(input_pdf) as doc:
        summary_df = mobius.extraction.summarise(doc)

    mobius.io.write_summary(summary_df, input_pdf, output_folder)


@cli.command(help="Produce full CSV of trend data from PDF/SVG input")
@click.argument("INPUT_PDF", type=click.Path(exists=True))
@click.argument("INPUT_SVG", type=click.Path(exists=True))
@click.argument("OUTPUT_FOLDER")
@click.option("-d", "--dates_file", help="Override date lookup file", default=None)
def full(input_pdf, input_svg, output_folder, dates_file=None):

    with mobius.io.open_document(input_pdf) as doc:
        summary_df = mobius.extraction.summarise(doc)

    data = mobius.graphs.graph_process(input_svg, None, False)

    date_lookup_df = mobius.io.read_dates_lookup(dates_file)

    svg_df = mobius.csv.process_all(data, date_lookup_df)

    result_df = pd.merge(
        summary_df, svg_df, left_on="plot_num", right_on="graph_num", how="outer"
    )

    mobius.extraction.validate(result_df)

    mobius.io.write_full_results(result_df, input_pdf, output_folder)


if __name__ == "__main__":
    cli()
