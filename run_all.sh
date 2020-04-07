#!/usr/bin/env bash
# Runs through all the SVG/PDF files available for download

set -e  # Exit on any error

COUNTRIES=$(./mobius.py svg | sed -En "s/.*[0-9 \.]+([A-Z]{2}(\-[A-Z][a-z]+)?).*/\1/p")

COUNTRIES=($COUNTRIES)

for COUNTRY in "${COUNTRIES[@]}"
do  
    echo Running for "${COUNTRY}"
    ./mobius.py download --svg "${COUNTRY}"
    ./mobius.py download --pdf "${COUNTRY}"

    if [[ $COUNTRY == "US-District" ]]; then
      echo "Change file name for District of Columbia PDF"
      mv pdfs/US-District_of_Columbia.pdf pdfs/US-District.pdf
    fi

    if [[ $COUNTRY == "US-New" ]]; then
      echo "Skip US-New issues with file downloads"
      continue
    fi

    if [[ $COUNTRY == "US-North" ]]; then
      echo "Skip US-North issues with file downloads"
      continue
    fi

    if [[ $COUNTRY == "US-Rhode" ]]; then
      echo "Change file name for Rhode Island PDF"
      mv pdfs/US-Rhode_Island.pdf pdfs/US-Rhode.pdf
    fi

    if [[ $COUNTRY == "US-South" ]]; then
      echo "Skip US-South issues with file downloads"
      continue
    fi

    if [[ $COUNTRY == "US-West" ]]; then
      echo "Change file name for US-West_Virginia PDF"
      mv pdfs/US-West_Virginia.pdf pdfs/US-West.pdf
    fi

    ./mobius.py full pdfs/"${COUNTRY}".pdf svgs/"${COUNTRY}".svg output
done
