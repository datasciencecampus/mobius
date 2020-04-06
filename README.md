# Mobility Report graph extractor (mobius)

<p align="center">
    <img src="/meta/logo.png" alt="Logo" height="100px">
</p>

For extracting **every** graph from **any** [Google's COVID-19 Community Mobility Report](https://www.google.com/covid19/mobility/) (182) into
comma separated value (CSV) files. This code is developed at _speed_ on the COVID-19 Community Mobility Report PDF documents published on Friday 3rd of April 2020. 

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

**TLDR:**

```shell
# check if your svg is available
python ./mobius.py svg

# check if your svg is available
python ./mobius.py download <COUNTRY_CODE>

# process it
python ./mobius.py proc <COUNTRY_CODE> <OUTPUT_FOLDER>
```

1. **Check for, and download, SVG and PDF files using `mobius.py svg` and `mobius.py download` commands**:

   Use the `mobius.py` command line tool to list all the available countries
   for SVGs and then download them with the two helpful commands below.

```text
Usage: mobius.py svg [OPTIONS]

  List all the SVGs available in the buckets

Options:
  --help  Show this message and exit.

Usage: mobius.py download [OPTIONS] COUNTRY_CODE

Options:
  -s, --svg  Download SVG of the country code
  -p, --pdf  Download PDF of the country code
  --help     Show this message and exit.
```

2. **Run the `mobius.py proc` command**

```text
Usage: mobius.py proc [OPTIONS] INPUT_LOCATION OUTPUT_FOLDER [DATES_FILE]

  Process a given country SVG

Options:
  -f, --folder TEXT  If provided will overwrite the output folder name
  -s, --svgs         Enables saving of SVGs that get extracted
  -c, --csvs         Enables saving of CSVs that get extracted
  -p, --plots        Enables creation and saving of additional PNG plots
  --help             Show this message and exit.
```

Specify the input file for the individual country as the `INPUT_LOCATION` and the
output folder where you want the CSV and other files to be saved to (e.g.
`./output`).

Optionally pass in a custom the dates lookup file (e.g.
`./config/dates_lookup.csv`) - used to convert coordinates to dates.

If you want simple matplotlib PNG plots to save as well as CSV files, use the `-p` flag.

## Data format

Each CSV will be saved to (`./output/<COUNTRY_CODE>/csv`), starting at `1.csv`. As of the **COVID-19 Community Mobility Reports** released on Friday 3rd April 2020, CSV files `1.csv` to `6.csv` relate to the country-level graphs in the original PDF (pages one and two). Then each set of 6 CSV files (e.g., `7.csv` to `12.csv`) will relate to a regional area.

Each set of 6 files follows the order:

1. Retail & recreation
2. Grocery & pharmacy
3. Parks
4. Transit stations
5. Workplaces
6. Residential

## G20 CSV Datasets

CSV datasets for G20 countries (except Russia and China) can be found at the [Data Science Campus' Google Mobility Reports Data repository](https://github.com/datasciencecampus/google-mobility-reports-data).

## Creating your own SVG

1. To create your own SVG from a PDF, we recommend using Affinity Designer. This is because Affinity Designer flattens the SVG, which is required for `mobius.py proc`. Affinity Designer also closes point features in SVG files, which other programmes do not. Use the following steps:

   1. Load in PDF document to Affinity Designer.
   1. Click Load all pages.
   1. `File > Export > SVG (for print)` if using **version 1.6.3** or `File > Export > SVG (digital - high quality)` for **version 1.8.3**
   1. Select Area: Whole Document.
   1. Save the SVG file to (`./svgs`).

## Contributing

Any suggestions or issues, please use the Issues template. We welcome
collaborators. To help us with this work, fork the repository and issue a Pull
Request when you have added a feature, or fixed a bug. Thanks!