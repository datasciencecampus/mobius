# stdlib
import os

# project
from .graphs import graph_process
from .csv import csv_process


def prep_output_folder(input_file, output_folder, overwrite_name):
    """Prepare the output folder. Creating required folder."""
    output_folder = (
        os.path.join(output_folder, overwrite_name)
        if overwrite_name
        else os.path.join(output_folder, input_file.split(".")[0].split("/")[-1])
    )
    try:
        os.mkdir(output_folder)
    except FileExistsError:
        print("Output folder exists, skip creation")
    return output_folder
