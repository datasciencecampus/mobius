# -*- coding: utf-8 -*-
import hashlib
import os

import click
import numpy as np
import pandas as pd


def _check_files_identical(previous_filepath, current_filepath):
    with open(previous_filepath, "rb") as f:
        previous_hash = hashlib.sha256(f.read()).hexdigest()

    with open(current_filepath, "rb") as f:
        current_hash = hashlib.sha256(f.read()).hexdigest()

    identical = previous_hash == current_hash

    print("Files are identical (hash match)")

    return identical


@click.command()
@click.argument("PREVIOUS_FILEPATH")
@click.argument("CURRENT_FILEPATH")
def main(previous_filepath, current_filepath):
    print(os.getcwd())
    print(f"Comparing runs: {previous_filepath} and {current_filepath}")

    identical = _check_files_identical(previous_filepath, current_filepath)

    if identical:
        return

    previous_df = pd.read_csv(previous_filepath)
    current_df = pd.read_csv(current_filepath)

    n_previous = len(previous_df)
    n_current = len(current_df)

    if n_current == n_previous:
        print(f"Same number of records: {n_current:,}")
    else:
        print(f"n_previous={n_previous:,}, n_current={n_current}:,")

    merged_df = pd.merge(previous_df, current_df, on=["page_num", "plot_num", "date"],
                         suffixes=("_prev", "_curr"))

    matching_values = np.sum(
        (merged_df.value_prev == merged_df.value_curr) |
        (merged_df.value_prev.isna() & merged_df.value_curr.isna())
    )

    print(f"Matching values: {matching_values:,}")

    differing = merged_df[
        (merged_df.value_prev != merged_df.value_curr) &
        (merged_df.value_prev.notna() | merged_df.value_curr.notna())
    ]

    print(f"Differing values: {len(differing):,}")

    print(differing.to_markdown())


if __name__ == "__main__":
    main()
