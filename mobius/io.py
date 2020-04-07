# -*- coding: utf-8 -*-
import os
from contextlib import contextmanager

import pandas as pd

__DEFAULT_DATES_LOOKUP_FILEPATH = os.path.join("config", "dates_lookup.csv")


def read_dates_lookup(filepath=None):
    if not filepath:
        filepath = __DEFAULT_DATES_LOOKUP_FILEPATH

    dates_lookup = pd.read_csv(filepath)
    return dates_lookup


def write_summary(df, input_pdf, output_folder):
    input_basename = os.path.basename(input_pdf)
    input_no_ext = os.path.splitext(input_basename)[0]
    out_filename = input_no_ext + "_summary.csv"

    outpath = os.path.join(output_folder, out_filename)
    df.to_csv(outpath, index=False)


def write_full_results(df, input_pdf, output_folder):
    input_basename = os.path.basename(input_pdf)
    input_no_ext = os.path.splitext(input_basename)[0]
    out_filename = input_no_ext + ".csv"

    outpath = os.path.join(output_folder, out_filename)

    relevant_columns = [
        "country",
        "plot_name",
        "page_num",
        "region",
        "plot_num",
        "asterisk",
        "date",
        "value",
        "headline",
    ]

    df[relevant_columns].to_csv(outpath, index=False)


@contextmanager
def open_document(filepath):

    f = open(filepath, "rb")
    yield f
    f.close()
