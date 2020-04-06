"""Extract subplots from whole pages/documents in SVG format."""
# stdlib
import os
import logging

# third party
import svgpathtools
from tqdm import tqdm


def graph_process(input_file, output_folder, save=True):
    """Split out subplots.

    If `save == True` peforms saving using `save_subplot`

    Outputs:
    {num, path_buffer}
    """

    # Variable that will encapsulate the results as the pipeline does its job
    OUTPUT = {}

    def state_change(path_type_name, state):
        return not path_type_name.startswith(state)

    def expected_trend_path(name, path_buffer):
        """Assuming after 5 horizontals we should switch to trend"""
        return name == "horizontal" and len(path_buffer) == 5

    def clear_buffer(num, path_buffer):
        """Clear the current buffer.

        Note: Assumes the next path will be a horizontal
        """
        if save:
            save_subplot(path_buffer, output_folder, num)

        OUTPUT[num] = path_buffer

        num += 1
        path_buffer = []
        state = "horizontal"
        return num, path_buffer, state

    logging.info(f"Processing {input_file}")

    paths, attributes = svgpathtools.svg2paths(input_file)

    relevant_elements = _extract_graph_components(attributes, paths)

    # This depends on the paths and attributes being in plot order
    # Assumes horizontals, followed by trend lines
    path_buffer = []

    state = "horizontal"
    num = 1

    for path_type_name, path, attribute in relevant_elements:

        if expected_trend_path(path_type_name, path_buffer):
            num, path_buffer, state = clear_buffer(num, path_buffer)

        if state_change(path_type_name, state):

            if state == "horizontal":
                state = "trend"
                assert len(path_buffer) == 5

            else:
                num, path_buffer, state = clear_buffer(num, path_buffer)

        path_buffer.append((path, attribute))

    if save:
        os.mkdir(f"{output_folder}/svg") if not os.path.exists(f"{output_folder}/svg") else False
        # TODO: see if this can be in clear buffer.
        # Don't forget the last graph in the buffer
        save_subplot(path_buffer, output_folder, num)

    OUTPUT[num] = path_buffer

    return OUTPUT


def save_subplot(path_buffer, output_folder, num):
    """Take all the paths in the buffer and save them to a new file"""
    logging.info(f"Saving sublot {num}")
    paths_to_save, attributes_to_save = tuple(zip(*path_buffer))
    svgpathtools.wsvg(
        paths_to_save, filename=os.path.join(output_folder, f"svg/{num}.svg"),
    )


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
