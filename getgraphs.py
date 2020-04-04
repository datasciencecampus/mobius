# stdlib
import os
import logging

# third party
import click
from svgpathtools import svg2paths2, wsvg


@click.command()
@click.argument("INPUT_LOCATION")
@click.argument("OUTPUT_FOLDER")
@click.option(
    "-m",
    "--multiple",
    is_flag=True,
    help="If the input location is a folder with multiple SVGs, this has to be set to true.",
)
@click.option(
    "-f",
    "--folder",
    help="If provided will overwrite the output folder name (can not be used with the `--multiple` flag)",
)
def main(input_location, output_folder, multiple, folder):
    if not multiple:
        process(input_location, output_folder, folder)
    else:
        files = [f for f in os.listdir(input_location) if f != ".DS_Store"]

        lst = []
        for file in files:
            lst.append(int(file.split(".")[0]))
        lst.sort()
        files = []
        for item in lst:
            files.append(f"{item}.svg")

        print("Converting:", *["  - " + file for file in files], sep="\n")
        for input_file in [os.path.join(input_location, file) for file in files]:
            try:
                process(input_file, output_folder)
            except Exception as e:
                print("Could not process file ", input_file, f"\nError: {e}", end="\n")


def process(input_file, output_folder, overwrite_name=None):
    hour_lines = []
    trends = []
    line_y = []
    trend_y = []
    trend_y_end = []
    paths_new = []
    attributes_new = []

    paths, attributes, svg_attributes = svg2paths2(input_file)

    # filter only relevant elements of the svg
    for k, v in enumerate(attributes):

        path = paths[k]
        if path._end is None:
            continue
        if v.get("style") is None:
            continue

        else:

            if "stroke:#dadce0" in v.get("style").split(";"):
                if "stroke-width:1.19px" in v.get("style").split(";"):
                    hour_lines.append(k)
                    paths_new.append(paths[k])
                    attributes_new.append(attributes[k])
            if "stroke:#4285f4" in v.get("style").split(";"):
                trends.append(k)
                paths_new.append(paths[k])
                attributes_new.append(attributes[k])

    # prep output folder
    output_folder = (
        os.path.join(output_folder, overwrite_name)
        if overwrite_name
        else os.path.join(output_folder, input_file.split(".")[0].split("/")[-1])
    )
    os.mkdir(output_folder)

    # FIX: missing one graph

    paths_save = []
    attributes_save = []

    count = 0

    for k, v in enumerate(attributes_new):

        # TODO This adds a horizontal line from the next graph, should be a better way
        if (
            (count + 1) % 6 == 0
            and count != 0
            and "stroke-width:1.19px" in attributes_new[count].get("style")
        ):
            attributes_new.append(attributes_new[len(attributes_new) - 1])
            attributes_new[k + 1 :] = attributes_new[k:-1]
            paths_new.append(paths_new[len(paths_new) - 1])
            paths_new[k + 1 :] = paths_new[k:-1]

        count = count + 1

    num = 1
    count = 0

    for k, v in enumerate(attributes_new):

        paths_save.append(paths_new[k])
        attributes_save.append(attributes_new[k])

        count = count + 1

        if count % 6 == 0:

            wsvg(
                paths_save,
                filename=os.path.join(output_folder, f"{num}.svg"),
                attributes=attributes_save,
            )
            paths_save = []
            attributes_save = []
            count = 0
            num += 1


if __name__ == "__main__":
    main()
