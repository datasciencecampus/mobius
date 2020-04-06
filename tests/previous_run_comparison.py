# -*- coding: utf-8 -*-
import hashlib
import os

import click
import numpy as np
import pandas as pd


@click.command()
@click.argument("PREVIOUS_DIR")
@click.argument("CURRENT_DIR")
def main(previous_dir, current_dir):
    print(f"Comparing runs from {previous_dir} and {current_dir}")
    print(os.getcwd())

    previous_filenames = set(os.listdir(previous_dir))
    current_filenames = sorted(os.listdir(current_dir))
    current_filenames_set = set(current_filenames)

    n_previous = len(previous_filenames)
    n_current = len(current_filenames)

    print(f"{n_current} current files")

    if n_current == n_previous:
        print("Same number of files")
    else:
        print(f"n_previous={n_previous}, n_current={n_current}")
        print(f"overlap={len(previous_filenames.intersection(current_filenames_set))}")

    hash_identical = 0
    value_identical = 0

    differing = []

    for current_filename in current_filenames:
        if current_filename in previous_filenames:

            with open(os.path.join(previous_dir, current_filename), "rb") as f:
                previous_hash = hashlib.sha256(f.read()).hexdigest()

            with open(os.path.join(current_dir, current_filename), "rb") as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()

            if previous_hash == current_hash:
                hash_identical += 1

            else:
                previous_df = pd.read_csv(os.path.join(previous_dir, current_filename))
                current_df = pd.read_csv(os.path.join(current_dir, current_filename))

                try:
                    pd.testing.assert_series_equal(
                        previous_df["value"], current_df["value"]
                    )
                    value_identical += 1
                except AssertionError:
                    differing.append((current_filename, previous_df, current_df))

    print(f"{hash_identical} hash identical files")

    print(f"{hash_identical + value_identical} value identical files")

    print(f"{len(differing)} shared files with differences")

    removed_single_identical = 0

    still_differing = []

    for fname, previous_df, current_df in sorted(differing):
        print(fname)
        remove_single_df = current_df.copy()
        remove_single_df["value_before"] = current_df["value"].shift(1)
        remove_single_df["value_after"] = current_df["value"].shift(-1)
        remove_single_df.loc[
            remove_single_df.value_before.isna() & remove_single_df.value_after.isna(),
            "value",
        ] = np.nan

        try:
            pd.testing.assert_series_equal(
                previous_df["value"], remove_single_df["value"]
            )
            removed_single_identical += 1
        except AssertionError:
            still_differing.append((fname, previous_df, current_df))

    print(
        f"{removed_single_identical} identical after removing single point data from current frame"
    )

    print(f"{len(still_differing)} still differing: {still_differing}")


if __name__ == "__main__":
    main()
