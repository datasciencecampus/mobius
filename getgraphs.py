# -*- coding: utf-8 -*-
"""Extract subplots from whole pages/documents in SVG format."""
import os

import click
import svgpathtools


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
        output_folder = _prep_output_folder(input_location, output_folder, folder)
        process(input_location, output_folder)
    else:
        files = [f for f in os.listdir(input_location) if not f.startswith(".")]

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
                output_folder = _prep_output_folder(input_location, output_folder, None)
                process(input_file, output_folder)
            except Exception as e:
                print("Could not process file ", input_file, f"\nError: {e}", end="\n")


def process(input_file, output_folder):
    """Split out subplots into separate files"""

    def state_change(path_type_name, state):
        return not path_type_name.startswith(state)

    def expected_trend_path(name, path_buffer):
        """Assuming after 5 horizontals we should switch to trend"""
        return name == "horizontal" and len(path_buffer) == 5

    def clear_buffer(num, path_buffer, save_subplot):
        """Clear the current buffer.

        Note: Assumes the next path will be a horizontal
        """
        save_subplot(path_buffer, num)
        num += 1
        path_buffer = []
        state = "horizontal"
        return num, path_buffer, state

    def save_subplot(path_buffer, num):
        """Take all the paths in the buffer and save them to a new file"""
        print(f"Saving sublot {num}")
        paths_to_save, attributes_to_save = tuple(zip(*path_buffer))
        svgpathtools.wsvg(
            paths_to_save,
            attributes=attributes_to_save,
            filename=os.path.join(output_folder, f"{num}.svg"),
        )

    print(f"Processing {input_file}")

    paths, attributes = svgpathtools.svg2paths(input_file)

    relevant_elements = _extract_graph_components(attributes, paths)

    # This depends on the paths and attributes being in plot order
    # Assumes horizontals, followed by trend lines
    path_buffer = []

    state = "horizontal"
    num = 1
    for path_type_name, path, attribute in relevant_elements:

        if expected_trend_path(path_type_name, path_buffer):
            num, path_buffer, state = clear_buffer(num, path_buffer, save_subplot)

        if state_change(path_type_name, state):

            if state == "horizontal":
                state = "trend"
                assert len(path_buffer) == 5

            else:
                num, path_buffer, state = clear_buffer(num, path_buffer, save_subplot)

        path_buffer.append((path, attribute))

    # Don't forget the last graph in the buffer
    save_subplot(path_buffer, num)


def _prep_output_folder(input_file, output_folder, overwrite_name):
    # prep output folder
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


def _extract_graph_components(attributes, paths):
    """Only keep lines of the svg related to the plots"""
    relevant_elements = []
    for path, attribute in zip(paths, attributes):

        if path._end is None:
            print("This does happen")
            continue

        style = attribute["style"]

        if style is None:
            continue

        if "stroke:#dadce0" in style and "stroke-width:1.19px" in style:
            relevant_elements.append(("horizontal", path, attribute))
            continue

        # Check for a blue path, or blue filled object
        if "stroke:#4285f4" in style:  # or ("fill:#4285f4" in style and :
            relevant_elements.append(("trend", path, attribute))
            continue

        if "fill:#4285f4" in style and isinstance(
            path[0], svgpathtools.path.CubicBezier
        ):
            relevant_elements.append(("trend_point", path, attribute))
            continue
    return relevant_elements


if __name__ == "__main__":
    main()
