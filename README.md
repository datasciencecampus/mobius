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
- Affinity Designer 1.6.5 and 1.8.3 ([Free 90 day trial link](https://affinity.serif.com/en-gb/90-day-affinity-trial/); [MacOS 1.6.5 Download link](https://d1gl0nrskhax8d.cloudfront.net/macos/designer/1.6.5/affinity-designer-1.6.5.135.dmg?Expires=1586019202&Signature=NV7XtRl5-d0NCYY4P0~VCJDzqrehVqE6T~~rrmEXULvjvkBE6KJc5iQH3ofR6FynCYrUbQFHpJjB1RA1thXqSSdv3NRAO7XFgH6o~B9G0B9U4Q9AcHDYODKaqW7AsK5c~bIu3NdN1Y9DRmm-9ve1fAll7BQ~et2D~KZHeEIz36oy3Qw13srZVFfXQ3g2ekn5Fb8IbH1GDOm3NZRS~tLutRaVnRg7x3d5WTmH5ncJB8i5GkS9b-DKzk961gn5SuqOWtm8WwaE7T~h-kzQJgPU9xqrfdT8QKwJ3wqb8W~DCDAKPSI~wnTXbWJZpE99MaSjZ-vY9jtDZg5SbXLAKfTH6g__&Key-Pair-Id=APKAIMMPYSI7GSVTEAAQ); [Windows 1.6.5 Download link](https://d1gl0nrskhax8d.cloudfront.net/windows/designer/1.6.5/affinity-designer-1.6.5.135.exe?Expires=1586019173&Signature=PAKJ2BnONNmv~oOXfHzAD2D08VTyrw4dFjci7pYjkvh0R2nK9FlfURQX1-VL9l3aYnYBdrkUK9wl-z52ONjrT84v0CODHTsF9mTn0iqaCOVhIVR-IDE4UkI7B3Rcv-vbAdFw8vh1YBdpQBkroxvuCjI8keCRA1htVndQhyBFDLRVDXPmdjDoCewWuESVF60~K35KffgD8kC5fB5BE~LPZOtcIxBPiQSL3nxZC9tARdiKfdEb9FED8zGACIEM9TSbw-KCiNaXrFDjWZi9roi1YkbsT~04Pjkf81pvVfBj2359jKR4TDd8QCmXWjc-6A7XJuhvh-8rwOtY2oUGoJ~RAA__&Key-Pair-Id=APKAIMMPYSI7GSVTEAAQ))
- Python 3

This code is developed at _speed_ on the COVID-19 Community Mobility Report PDF documents published on Friday 3rd of April 2020. Changes may be made.

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
./mobius.py svg

# check if your svg is available
./mobius.py download <COUNTRY_CODE>

# process it
./mobius.py proc -c <COUNTRY_CODE> <OUTPUT_FOLDER>
```

1. Either create, or download a pre-made, SVG document file (this file is the
   entire PDF document in Scalable Vector Graphics (SVG) format).

   **Create**:

   1. Load in PDF document to Affinity Designer.
   1. Click Load all pages.
   1. `File > Export > SVG (for print)` if using **version 1.6.3** or `File > Export > SVG (digital - high quality)` for **version 1.8.3**
   1. Select Area: Whole Document.
   1. Save the SVG file to (`./svgs`).

   **Download**:

   Use the `mobius.py` command line tool to list all the available countries
   for SVGs and then download them with the two helpful commands below

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

```

```
