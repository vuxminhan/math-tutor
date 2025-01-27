#!/usr/bin/env bash

# Name of the input file
input="wrong_ans_all_cases.txt"

# While reading each line (testID questionID) from the file:
while IFS=$'\t' read -r testID questionID; do
    
    # -----------------------------------
    # Example line:
    # testID="13-11-08-A"   questionID="Q4"
    # -----------------------------------
    
    # 1) Extract prefix and letter:
    prefix="${testID%-*}"    # e.g. "13-11-08"
    letter="${testID##*-}"   # e.g. "A"
    
    # 2) Extract just the question number (removing the leading 'Q'):
    questionNum="${questionID#Q}"   # e.g. "Q4" => "4"
    
    # 3) Define source path (from ../mathematics-full-images):
    #    e.g. "../mathematics-full-images/13-11-08/A-Test/4.md"
    #    Note that "A-Test" is capital "T" in source.
    srcDir="../mathematics-full-images/$prefix/${letter}-Test"
    srcFile="$srcDir/${questionNum}.md"
    
    # 4) Define destination path:
    #    e.g. "../mathematics-retry-o1/13-11-08/A-test/4.md"
    #    Note that we use lowercase "test" here.
    dstDir="../mathematics-retry-o1/$prefix/${letter}-test"
    dstFile="$dstDir/${questionNum}.md"
    
    # 5) Create the destination folder (if it doesn't exist)
    mkdir -p "$dstDir"
    
    # 6) Copy the .md file from source to destination
    if [ -f "$srcFile" ]; then
        cp "$srcFile" "$dstFile"
        echo "Copied: $srcFile -> $dstFile"
    else
        echo "WARNING: Source file not found: $srcFile"
    fi

    # 7) Copy the entire Images folder if it exists
    #    e.g. "../mathematics-full-images/13-11-08/Images" -> "../mathematics-retry-o1/13-11-08/Images"
    srcImageDir="../mathematics-full-images/$prefix/Images"
    dstImageDir="../mathematics-retry-o1/$prefix/"

    if [ -d "$srcImageDir" ]; then
        mkdir -p "$dstImageDir"
        cp -R "$srcImageDir/" "$dstImageDir/"
        echo "Copied images from $srcImageDir -> $dstImageDir"
    else
        echo "No images folder found for $prefix"
    fi

done < "$input"
