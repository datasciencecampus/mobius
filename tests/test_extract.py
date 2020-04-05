# -*- coding: utf-8 -*-
from svgpathtools import svg2paths
import createcsvs


def test_categorise_paths():
    # Given
    filepath = "resources/nogaps.svg"

    # When
    paths, _ = svg2paths(filepath)
    xlim, lines, trend = createcsvs.categorise_paths(paths)

    # Then
    assert len(lines) == 3


def test_convert_units():
    # Given
    filepath = "resources/nogaps.svg"

    # When
    paths, _ = svg2paths(filepath)
    xlim, lines, trend = createcsvs.categorise_paths(paths)
    trend_converted = createcsvs.convert_units(trend, lines, xlim, yspan=80, xspan=42)

    # Then
    assert len(trend_converted) == 43


def test_convert_units_w_gaps():
    # Given
    filepath = "resources/gaps.svg"

    # When
    paths, _ = svg2paths(filepath)
    xlim, lines, trend = createcsvs.categorise_paths(paths)
    trend_converted = createcsvs.convert_units(trend, lines, xlim, yspan=80, xspan=42)

    # Then
    assert len(trend_converted) == 27


def test_path_with_point_at_end():
    # Given
    filepath = "resources/endpoint.svg"

    # When
    paths, _ = svg2paths(filepath)
    xlim, lines, trend = createcsvs.categorise_paths(paths)

    # Then
    assert len(trend) == 26


def test_path_with_points_in_middle():
    # Given
    filepath = "resources/midpoints.svg"

    # When
    paths, _ = svg2paths(filepath)
    xlim, lines, trend = createcsvs.categorise_paths(paths)

    # Then
    assert len(trend) == 9
