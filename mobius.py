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


def show_dates():
    dates = []
    blobs = list(get(filetype='PDF'))
    for i, blob in enumerate(blobs):
        date = blob.name.split("/")[-1].split('_')[0]
        if blob.name.split("/")[-1].split('_')[0] not in dates:
            dates.append(blob.name.split("/")[-1].split('_')[0])
            print(f"{date}")


def show(filetype, date):
    url_prefix = "https://storage.cloud.google.com/mobility-reports/"
    country_names = pd.read_csv(os.path.join(os.getcwd(),'config/country_codes.csv'))
    MAXLEN = 25
    MAXLEN_COUNTRY = 40
    blobs = list(get(filetype=filetype))
    print("Available countries:")
    if date is not None:
        for i, blob in enumerate(blobs):
            if blob.name.split("/")[-1].split('_')[0] == date:
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
                print(f" {iteration}. {country} {country_name}  {date}  ({url_prefix + blob.name})")

    else:
        print('x')
        for i, blob in enumerate(blobs):
            pdf_date = blob.name.split("/")[-1].split('_')[0]
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
            print(f" {iteration}. {country} {country_name}  {pdf_date}   ({url_prefix + blob.name})")


@click.group(help="Downloader and processor for Google mobility reports")
def cli():
    pass


@cli.command(help="List all the dates reports are available for")
def dt():
    show_dates()


@cli.command(help="List all the SVGs available in the buckets")
@click.argument("DATE", required = False)
def svg(date):
    show("SVG", date)


@cli.command(help="List all the PDFs available in the buckets")
@click.argument("DATE", required=False)
def pdf(date):
    show("PDF", date)


@cli.command(help="Download pdf and svg for a given country using the country code")
@click.argument("COUNTRY_CODE")
@click.argument("DATE", required = False)
def download(country_code, date):
    client = Client.create_anonymous_client()

    def _download(blobs, extension, date):

        download_count = 0

        if len(blobs) and date is not None:
            for blob in blobs:
                if blob.name.split("/")[-1].split('_')[0] == date:
                    fname = f"{extension}s/{get_country(blob)}_{date}.{extension}"
                    with open(fname, "wb+") as fileobj:

                        client.download_blob_to_file(blob, fileobj)

                    print(
                        f"Download {country_code} {date} {extension} complete. Saved to /{extension}s"
                    )
                    download_count += 1

        if len(blobs) and date == None:
            for blob in blobs:
                pdf_date = blob.name.split("/")[-1].split('_')[0]
                fname = f"{extension}s/{get_country(blob)}_{pdf_date}.{extension}"
                with open(fname, "wb+") as fileobj:

                    client.download_blob_to_file(blob, fileobj)

                print(
                    f"Download {country_code}_{pdf_date} {extension} complete. Saved to /{extension}s"
                )
                download_count += 1

        if download_count == 0:
            print(f"Could not find a {extension} file for code {country_code}")

    regex = f"\d{{4}}-\d{{2}}-\d{{2}}_{country_code}_M.+"

    blobs = get(filetype="SVG", regex=regex)
    _download(blobs, "svg", date)

    blobs = get(filetype="PDF", regex=regex)
    _download(blobs, "pdf", date)


@cli.command(help="Process a given country SVG")
@click.argument("INPUT_LOCATION")
@click.argument("OUTPUT_FOLDER")
@click.argument("DATES_FILE")
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
def full(input_pdf, input_svg, output_folder):

    with mobius.io.open_document(input_pdf) as doc:
        summary_df = mobius.extraction.summarise(doc)

    data = mobius.graphs.graph_process(input_svg, None, False)

    date_lookup_df = mobius.extraction.create_date_lookup(summary_df)

    svg_df = mobius.csv.process_all(data, date_lookup_df)

    result_df = pd.merge(
        summary_df, svg_df, left_on="plot_num", right_on="graph_num", how="outer"
    )

    mobius.extraction.validate(result_df)

    mobius.io.write_full_results(result_df, input_pdf, output_folder)


if __name__ == "__main__":
    cli()
