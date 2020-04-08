#!/usr/bin/env bash
# Runs through all the SVG/PDF files available for download

# Default mode run both full and summary
MODE=ALL

# Set mode if full/summary passed
if [ $# -eq 1 ]
  then
    if [ "$1" = "full" ]; then
      MODE=FULL
    elif [ "$1" = "summary" ]; then
      MODE=SUMMARY
    else
      echo "Unexpected input, supports: summary, full (or none)"
      exit 1
    fi
fi

set -e  # Exit on any error

# List all the countries
COUNTRIES=$(./mobius.py ls | sed -En "s/.*[0-9 \.]+([A-Z]{2}(\-[A-Z][a-z]+)?).*/\1/p")

COUNTRIES=($COUNTRIES)

for COUNTRY in "${COUNTRIES[@]}"
do  
    echo Running for "${COUNTRY}"

    # Download pdf and svg
    ./mobius.py download "${COUNTRY}"

    case $MODE in
      ALL)
        echo "Running summary and full"
        ./mobius.py summary pdfs/"${COUNTRY}".pdf output
        ./mobius.py full pdfs/"${COUNTRY}".pdf svgs/"${COUNTRY}".svg output
        ;;

      SUMMARY)
        echo "Running summary only"
        ./mobius.py summary pdfs/"${COUNTRY}".pdf output
        ;;

      FULL)
        echo "Running full only"
        ./mobius.py full pdfs/"${COUNTRY}".pdf svgs/"${COUNTRY}".svg output
        ;;
    esac
done

echo "Script finished."
