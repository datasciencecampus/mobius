# -*- coding: utf-8 -*-
import pandas as pd
import pytest

import mobius


def test_create_date_lookup_data_issue_raises():
    # Given
    summary_df = pd.DataFrame({
        "date_string": ["April 24, 2020", "April 24, 2020"],
        "xlabels": [("24 April", "25 April", "26 April"),
                    ("24 April", "25 April", "27 April"),]
    })

    with pytest.raises(ValueError):
        mobius.extraction.create_date_lookup(summary_df)


def test_create_date_lookup_data():
    # Given
    summary_df = pd.DataFrame({
        "date_string": ["March 29, 2020"] * 2,
        "xlabels": [("Sun Feb 16", "Sun March 8", "Sun March 29")] * 2
    })

    # When
    lookup_df = mobius.extraction.create_date_lookup(summary_df)

    # Then
    assert len(lookup_df) > 0

    assert "index" in lookup_df.columns
    assert "date" in lookup_df.columns

    assert len(lookup_df) == 43

    assert lookup_df.loc[0, "index"] == 1
    assert lookup_df.loc[42, "index"] == 43

    assert lookup_df.loc[0, "date"] == "2020-02-16"
    assert lookup_df.loc[42, "date"] == "2020-03-29"


def test_create_date_lookup_sinlge_digit_date():
    # Given
    summary_df = pd.DataFrame({
        "date_string": ["March 29, 2020"] * 2,
        "xlabels": [("Sun March 8", "Sun March 29")] * 2
    })

    # When
    lookup_df = mobius.extraction.create_date_lookup(summary_df)

    # Then
    assert lookup_df.loc[0, "date"] == "2020-03-08"
