#!/usr/bin/env bash
# Runs through all the SVG/PDF files available for download

set -e  # Exit on any error

COUNTRIES=$(./mobius.py svg | sed -En "s/.*[0-9 \.]+([A-Z]{2}).*/\1/p")

COUNTRIES=($COUNTRIES) 

for COUNTRY in "${COUNTRIES[@]}"
do  
    echo Running for "${COUNTRY}"
    ./mobius.py download --svg "${COUNTRY}"
    ./mobius.py download --pdf "${COUNTRY}"
    ./mobius.py full pdfs/"${COUNTRY}".pdf svgs/"${COUNTRY}".svg output
    
done
