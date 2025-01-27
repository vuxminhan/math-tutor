#!/usr/bin/env bash

# The final merged output file
OUTPUT_FILE="merged_mathematics_all.md"

# 1. Remove old output if it exists (to avoid appending multiple times)
rm -f "$OUTPUT_FILE"

# 2. Loop through any folder named like '13-11-08', '14-01-22', etc. in the "mathematics" folder
for date_dir in mathematics/[0-9][0-9]-[0-9][0-9]-[0-9][0-9]; do
  # If there's no match or it's not a directory, skip it
  [ -d "$date_dir" ] || continue

  # 3. Find all .md files within this directory and merge them into OUTPUT_FILE
  find "$date_dir" -type f -name "*.md" | while IFS= read -r file; do
    # Create a base name for display by removing the leading "mathematics/"
    # and replacing any "/" in the rest of the path with "-"
    # e.g., "mathematics/13-11-08/A-Test/1.md" becomes "13-11-08-A-Test-1.md"
    base_name="$(echo "$file" | sed 's|^mathematics/||; s|/|-|g')"

    # 4. Append a header to show which file is being concatenated
    echo "## File: $base_name" >> "$OUTPUT_FILE"
    echo >> "$OUTPUT_FILE"

    # 5. Append the actual content of the file
    cat "$file" >> "$OUTPUT_FILE"

    # 6. Insert a separator between files
    echo -e "\n---\n" >> "$OUTPUT_FILE"
  done
done

echo "All markdown files have been merged into '$OUTPUT_FILE'."
