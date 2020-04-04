# Mobility Report graph extractor

<p align="center">
    <img src="/meta/logo.png" alt="Logo">
</p>

For extracting graphs from COVID-19 Community Mobility Report PDF into
comma separated value (CSV) files for each graph. 

Scripts `getgraphs.py` and `createcsvs.py` are able to extract all graphs from a Scalable Vector Graphics (SVG) document (converted as a single document from the original PDF) in one go, including those with gaps in the data.

**Developed and tested with:**
- MacOS 10.15.4
- PyCharm Community Edition 2018.3.2
- Affinity Designer 1.6.5
- Python 3

This code is developed at *speed* on the COVID-19 Community Mobility Report PDF documents published on Friday 3rd of April 2020. Changes may be made.

## Installation

We provide the python `requirements.txt` file as well as a `poetry` setup for
dependency management.

We recommend using a virtual environment before installing dependencies.

To install with `pip`:

```shell
pip install -r requirements.txt
```

To install with `poetry`

```shell
poetry install
```

## Usage

1. Either create, or download a pre-made, SVG document file (this file is the
   entire PDF document in Scalable Vector Graphics (SVG) format).

   **Create**:

   1. Load in PDF document to Affinity Designer.
   1. Click Load all pages.
   1. `File > Export > SVG (for print)`
   1. Select Area: Whole Document.
   1. Save the SVG file to (`./svgs`).

   **Download**:

   1. The Data Science Campus has created [SVGs for all G20 countries](https://drive.google.com/open?id=1n5XXYbJtf-wNWEkDPe7N8iNfjzJXwZ_d) (no PDFs available for China or Russia).
   1. Save the SVG file to (`./svgs`).

2. **Run the `getgraphs.py` Python script.**

```text
Usage: getgraphs.py [OPTIONS] INPUT_LOCATION OUTPUT_FOLDER

Options:
  -m, --multiple     If the input location is a folder with multiple SVGs,
                     this has to be set to true.
  -f, --folder TEXT  If provided will overwrite the output folder name (can
                     not be used with the `--multiple` flag)
  --help             Show this message and exit.
```

Specify either the location of the single SVG file (e.g. `./svgs/UK`) you with to process or the folder of svg files (you will have to provide the `-m` flag in that case). You will also have to provide the output folder, e.g. `./graphs/UK`.

3. **Run the `createcsvs.py` Python script.**

```text
Usage: createcsvs.py [OPTIONS] INPUT_FOLDER OUTPUT_FOLDER DATES_FILE

Options:
  -p, --plots  Enables creation and saving of additional PNG plots
  --help       Show this message and exit.
```

Specify the input folder where the individual SVG files are (e.g. `./graphs/UK`),
the output folder where you want the CSV files to be saved to (e.g. `./output/UK`),
and the dates lookup file (e.g. `./config/dates_lookup.csv`) - used to convert
coordinates to dates.

If you want simple matplotlib PNG plots to save as well as CSV files, use the `-p` flag.

## Data format

Each CSV will be saved to (`./output/subfolder`), starting at `1.csv`. As of the **COVID-19 Community Mobility Reports** released on Friday 3rd April 2020, CSV files `1.csv` to `6.csv` relate to the country-level graphs in
the original PDF (pages one and two). Then each set of 6 CSV files (e.g., `7.csv` to `12.csv`) will relate to a regional area.

Each set of 6 files follows the order:

1. Retail & recreation
2. Grocery & pharmacy
3. Parks
4. Transit stations
5. Workplaces
6. Residential

## United Kingdom Dataset

A pre-made dataset for the United Kingdom can be found at the [Data Science Campus' Google Mobility Reports Data repository](https://github.com/datasciencecampus/google-mobility-reports-data).


## Contributing

Any suggestions or issues, please use the Issues template. We welcome
collaborators. To help us with this work, fork the repository and issue a Pull
Request when you have added a feature, or fixed a bug. Thanks!
