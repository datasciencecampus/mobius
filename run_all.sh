#!/usr/bin/env bash
# Runs through all the SVG/PDF files available for download

# Help and usage
help () {
	cat << EOF
written by Data Science Campus <datasciencecampus@ons.gov.uk>

run_all.sh [COMMAND] DATE [STATES]

Commands

    full    - run both the extraction and summary
    summary - run just the summary
    help    - prints this help text

Date format: yyyy-mm-dd (Note: passing a date is mandatory at the moment)

STATES - by passing \`true\` as the value for STATES, it will run on
         US states instead.

e.g. 1. run_all.sh full 2020-04-05      # runs all countries for that period
     2. run_all.sh full 2020-04-05 true # runs all US states for that date

EOF
exit 0
}

# Default mode run both full and summary
MODE=ALL

# Set mode if full/summary passed
case $1 in 
	full) 
    MODE=FULL
    DATE=$2
    STATES=$3
    ;;
	summary) 
    MODE=SUMMARY
    DATE=$2
    STATES=$3
    ;;
	help) 
        help 
        ;;
	*) 
    DATE=$1
    STATES=$2
    ;;
esac

set -e  # Exit on any error

# Get dates lookup
CLEAN=$(echo $DATE | sed -r 's/\-/_/g')
DATES_FILE="config/dates_lookup_${CLEAN}.csv"
echo "Using $DATES_FILE as lookup"

# List all the countries/states
case $STATES in 
    true)
    COUNTRIES=$(./mobius.py svg | sed -En "s/.*[0-9 \.]+([US-]{2}(\-[A-Z][A-Za-z_]+)).*/\1/p")

    ;;
    *)
    COUNTRIES=$(./mobius.py svg | sed -En "s/.*[0-9 \.]+([A-Z]{2}(\-[A-Z][A-Za-z_]+)?).*/\1/p")
    ;;
esac

COUNTRIES=($COUNTRIES)

full () {
    ./mobius.py full pdfs/"${1}_${DATE}".pdf svgs/"${1}_${DATE}".svg output $DATES_FILE
}

summary () {
    ./mobius.py summary pdfs/"${1}_${DATE}".pdf output $DATES_FILE
}


for COUNTRY in "${COUNTRIES[@]}"
do
        echo Running for $COUNTRY $DATE

        # Download pdf and svg
        ./mobius.py download $COUNTRY $DATE

        case $MODE in
          ALL)
            echo "Running summary and full"
            full $COUNTRY 
            summary $COUNTRY 
            ;;

          SUMMARY)
            echo "Running summary only"
            summary $COUNTRY
            ;;

          FULL)
            echo "Running full only"
            full $COUNTRY 
            ;;
        esac
done

echo "Script finished."
