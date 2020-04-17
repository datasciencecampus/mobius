# -*- coding: utf-8 -*-
from svgpathtools.path import Path, Line

import mobius


def test_single_segment_lines():
    # Given
    paths = [
        (Path(Line(start=(24058.2+8686.78j), end=(24534.52+8686.78j))), None),  # horizontal line - bottom
        (Path(Line(start=(24058.2+8627.24j), end=(24534.52+8627.24j))), None),  # horizontal line
        (Path(Line(start=(24058.2+8567.7j), end=(24534.52+8567.7j))), None),  # horizontal line - baseline
        (Path(Line(start=(24058.2+8508.16j), end=(24534.52+8508.16j))), None),  # horizontal line
        (Path(Line(start=(24058.2+8448.62j), end=(24534.52+8448.62j))), None),  # horizontal line - top
        (Path(Line(start=(24523.2+8664.45j), end=(24534.54+8663.114000000001j))), None)]  # Trend line

    date_lookup = mobius.io.read_dates_lookup(filepath="../config/dates_lookup_2020_03_29.csv")

    # When
    df = mobius.csv.csv_process(paths, 1, date_lookup, output_folder=None, plots=False, save=None)

    # Then
    assert round(df.at[42, "value"]) == -64
