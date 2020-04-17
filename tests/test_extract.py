# -*- coding: utf-8 -*-
from svgpathtools import svg2paths
import mobius


def test_categorise_paths():
    # Given
    filepath = "resources/nogaps.svg"

    # When
    paths = svg2paths(filepath)
    paths = list(zip(*paths))
    xlim, lines, trend = mobius.csv.categorise_paths(paths, "1", None)

    # Then
    assert len(lines) == 3


def test_convert_units():
    # Given
    filepath = "resources/nogaps.svg"

    # When
    paths = svg2paths(filepath)
    paths = list(zip(*paths))
    xlim, lines, trend = mobius.csv.categorise_paths(paths, "1", None)
    trend_converted = mobius.csv.convert_units(trend, lines, xlim, yspan=80, xspan=42)

    # Then
    assert len(trend_converted) == 43


def test_convert_units_w_gaps():
    # Given
    filepath = "resources/gaps.svg"

    # When
    paths = svg2paths(filepath)
    paths = list(zip(*paths))
    xlim, lines, trend = mobius.csv.categorise_paths(paths, "1", None)
    trend_converted = mobius.csv.convert_units(trend, lines, xlim, yspan=80, xspan=42)

    # Then
    assert len(trend_converted) == 27


def test_path_with_point_at_end():
    # Given
    filepath = "resources/endpoint.svg"

    # When
    paths = svg2paths(filepath)
    paths = list(zip(*paths))
    xlim, lines, trend = mobius.csv.categorise_paths(paths, "1", None)

    # Then
    assert len(trend) == 26


def test_path_with_points_in_middle():
    # Given
    filepath = "resources/midpoints.svg"

    # When
    paths = svg2paths(filepath)
    paths = list(zip(*paths))
    xlim, lines, trend = mobius.csv.categorise_paths(paths, "1", None)

    # Then
    assert len(trend) == 9


def test_path_only_individual_points():
    # Given
    filepath = "resources/no_segment_trendline.svg"

    # When
    paths = svg2paths(filepath)
    paths = list(zip(*paths))
    xlim, lines, trend = mobius.csv.categorise_paths(paths, "1", None)

    # Then
    assert len(trend) == 3


def test_path_single_line_segment():
    # Given
    filepath = "resources/single_segment_trendline.svg"

    # When
    paths = svg2paths(filepath)
    paths = list(zip(*paths))
    xlim, lines, trend = mobius.csv.categorise_paths(paths, "1", None)

    # Then
    assert len(trend) == 2
