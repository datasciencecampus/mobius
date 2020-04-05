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
        process(input_location, output_folder, folder)
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
                process(input_file, output_folder)
            except Exception as e:
                print("Could not process file ", input_file, f"\nError: {e}", end="\n")


def process(input_file, output_folder, overwrite_name=None):

    paths, attributes = svgpathtools.svg2paths(input_file)

    relevant_elements = []

    # filter only relevant elements of the svg
    for path, attribute in zip(paths, attributes):

        if path._end is None:
            continue

        style = attribute["style"]

        if style is None:
            continue

        if "stroke:#dadce0" in style and "stroke-width:1.19px" in style:
            relevant_elements.append(("horizontal", path.start, path, attribute))
            continue

        # Check for a blue path, or blue filled object
        if "stroke:#4285f4" in style: # or ("fill:#4285f4" in style and :
            relevant_elements.append(("trend", path.start, path, attribute))
            continue

        if "fill:#4285f4" in style and isinstance(path[0], svgpathtools.path.CubicBezier):
            relevant_elements.append(("trend_point", path.start, path, attribute))
            continue

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

    # ordering dependent saving of elements to separate graphs
    path_buffer = []

    state = "horizontal"
    num = 1
    for name, _, path, attribute in relevant_elements:

        if name == "horizontal" and len(path_buffer) == 5:
            paths_to_save, attributes_to_save = tuple(zip(*path_buffer))
            svgpathtools.wsvg(paths_to_save, attributes=attributes_to_save,
                              filename=os.path.join(output_folder, f"{num}.svg"))

            num += 1
            path_buffer = []
            state = "horizontal"

        if not name.startswith(state):

            if state == "horizontal":
                state = "trend"
                assert len(path_buffer) == 5

            else:
                paths_to_save, attributes_to_save = tuple(zip(*path_buffer))
                svgpathtools.wsvg(paths_to_save, attributes=attributes_to_save,
                                  filename=os.path.join(output_folder, f"{num}.svg"))

                num += 1
                path_buffer = []
                state = "horizontal"

        path_buffer.append((path, attribute))

    paths_to_save, attributes_to_save = tuple(zip(*path_buffer))
    svgpathtools.wsvg(paths_to_save, attributes=attributes_to_save,
                      filename=os.path.join(output_folder, f"{num}.svg"))


if __name__ == "__main__":
    main()
