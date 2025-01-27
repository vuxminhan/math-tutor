#!/usr/bin/env bash

# Directory containing the CSV files
INPUT_DIR="metadata"

# The merged output file
OUTPUT_FILE="AI_score_merged.csv"

# Remove the output file if it exists, to start fresh
rm -f "$OUTPUT_FILE"

# A flag to indicate if we've already saved the header
headerSaved=false

# Loop through all CSV files matching AI_score_*.csv
for file in "$INPUT_DIR"/AI_score_*.csv; do
  
  # If we haven't saved a header yet, copy the entire file (including header)
  if [ "$headerSaved" = false ]; then
    cat "$file" > "$OUTPUT_FILE"
    headerSaved=true

  # If we already have a header, skip the first line of the file
  else
    # tail -n +2 means skip the first line and append everything else
    tail -n +2 "$file" >> "$OUTPUT_FILE"
  fi

done

echo "All AI_score_*.csv files from ${INPUT_DIR} have been merged into ${OUTPUT_FILE}."
