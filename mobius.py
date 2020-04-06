# -*- coding: utf-8 -*-
# stdlib
import os
import logging

# third party
import click
import pandas as pd
from tqdm import tqdm

# project
from mobius import graph_process, csv_process, prep_output_folder


@click.command()
@click.argument("INPUT_LOCATION")
@click.argument("OUTPUT_FOLDER")
@click.argument("DATES_FILE", default="config/dates_lookup.csv")
@click.option(
    "-f",
    "--folder",
    help="If provided will overwrite the output folder name (can not be used with the `--multiple` flag)",
)
@click.option(
    "-s", "--svgs", help="Enables saving of svgs that get extracted", is_flag=True,
)
@click.option(
    "-c", "--csvs", help="Enables saving of csvs that get extracted", is_flag=True,
)
@click.option(
    "-p",
    "--plots",
    is_flag=True,
    help="Enables creation and saving of additional PNG plots",
)
def main(input_location, output_folder, folder, dates_file, svgs, csvs, plots):

    date_lookup_df = pd.read_csv(dates_file)

    print(f"Processing {input_location}")
    output_folder = prep_output_folder(input_location, output_folder, folder)
    data = graph_process(input_location, output_folder, svgs)

    iterable = tqdm(data.items())
    return [
        csv_process(paths, num, date_lookup_df, output_folder, plots=plots, save=csvs)
        for num, paths in iterable
    ]


if __name__ == "__main__":
    main()
