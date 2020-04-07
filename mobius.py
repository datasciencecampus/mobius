#!/usr/bin/env python3

# stdlib
import re
import os
import logging

# third party
import click
import pandas as pd
from tqdm import tqdm
from google.cloud.storage.client import Client

# project
from mobius import graph_process, csv_process, prep_output_folder

SVG_BUCKET = "mobility-reports"


def get(filetype="SVG", regex="\d{4}-\d{2}-\d{2}_.+"):
    client = Client.create_anonymous_client()
    blobs = filter(
        lambda b: re.match(f"{filetype}/{regex}", b.name),
        client.list_blobs(SVG_BUCKET),
    )
    return list(blobs)


def get_country(blob):
    name = blob.name.split("/")[-1]
    country = name.replace("Mobility_Report_en", "")[11:-5]
    return country


def show(filetype):
    MAXLEN = 20
    blobs = list(get(filetype=filetype))
    print("Available countries:")
    for i, blob in enumerate(blobs):
        country = get_country(blob)
        country = (
            country + (" " * (MAXLEN - len(country)))
            if len(country) < MAXLEN
            else country[:MAXLEN]
        )
        iteration = str(i + 1)
        iteration = (
            iteration
            if (len(iteration) == 3)
            else (" " * (3 - len(iteration)) + iteration)
        )
        print(f" {iteration}. {country} ({blob.name})")


@click.group(help="Downloader and processor for Google mobility reports")
def cli():
    pass


@cli.command(help="List all the SVGs available in the buckets")
def svg():
    show("SVG")


@cli.command(help="List all the PDFs available in the buckets")
def pdf():
    show("PDF")


@cli.command(help="Download svg for a given country using the country code")
@click.argument("COUNTRY_CODE")
@click.option(
    "-s", "--svg", help="Download SVG of the country code", is_flag=True, default=True,
)
@click.option(
    "-p", "--pdf", help="Download PDF of the country code", is_flag=True,
)
def download(country_code, svg, pdf):
    client = Client.create_anonymous_client()

    def _download(blobs, svg):
        if len(blobs):
            for blob in blobs:
                extension = "svg" if svg else "pdf"
                fname = f"{extension}s/{get_country(blob)}.{extension}"
                with open(fname, "wb+") as fileobj:
                    client.download_blob_to_file(blob, fileobj)

            print(
                f"Download {country_code} {extension} complete. Saved to /{extension}s"
            )
        else:
            print(f"Could not find a {extension} file for code {country_code}")

    if svg:
        regex = f"\d{{4}}-\d{{2}}-\d{{2}}_{country_code}_.+"
        blobs = get(filetype="SVG", regex=regex)
        _download(blobs, True)
    if pdf:
        regex = f"\d{{4}}-\d{{2}}-\d{{2}}_{country_code}_.+"
        blobs = get(filetype="PDF", regex=regex)
        _download(blobs, False)


@cli.command(help="Process a given country SVG")
@click.argument("INPUT_LOCATION")
@click.argument("OUTPUT_FOLDER")
@click.argument("DATES_FILE", default="config/dates_lookup.csv")
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

    date_lookup_df = pd.read_csv(dates_file)

    print(f"Processing {input_location}")
    output_folder = prep_output_folder(input_location, output_folder, folder)
    data = graph_process(input_location, output_folder, svgs)

    iterable = tqdm(data.items())
    return [
        csv_process(paths, num, date_lookup_df, output_folder, plots=plots, save=True)
        for num, paths in iterable
    ]


if __name__ == "__main__":
    cli()
