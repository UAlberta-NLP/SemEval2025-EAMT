import argparse
import os
import json
import pandas as pd

def process_files(root_folder, excel_file, output_file):
    # Load the Excel file with multiple sheets
    excel_data = pd.ExcelFile(excel_file)

    # Initialize a dictionary to store the results
    results = {}

    # Iterate through all JSONL files in the root folder
    for filename in os.listdir(root_folder):
        if filename.endswith(".jsonl"):
            jsonl_path = os.path.join(root_folder, filename)
            base_name = os.path.splitext(filename)[0]

            # Check if a corresponding sheet exists in the Excel file
            if base_name in excel_data.sheet_names:
                # Load the sheet into a DataFrame
                df = excel_data.parse(sheet_name=base_name)

                # Load the JSONL file
                with open(jsonl_path, 'r', encoding='utf-8') as f:
                    jsonl_data = [json.loads(line) for line in f]
 
                # Initialize match counters
                label_match = 0
                aka_match = 0
 
                # Iterate over rows in the DataFrame
                for _, row in df.iterrows():
                    row_id = row['id']
                    labels = str(row['Label ']).split(';') if pd.notna(row['Label ']) else []
                    aka_labels = str(row['Also known as ']).split(';') if pd.notna(row['Also known as ']) else []
 
                    # Find the corresponding JSONL entry by ID
                    jsonl_entry = next((entry for entry in jsonl_data if entry['id'] == row_id), None)
                    if jsonl_entry:
                        mentions = [t['mention'] for t in jsonl_entry['targets']]
 
                        # Check for label matches
                        if any(label.strip() in mentions for label in labels):
                            label_match += 1
 
                        # Check for AKA matches
                        if any(aka.strip() in mentions for aka in aka_labels):
                            aka_match += 1
 
                # Calculate match percentages
                total_rows = len(df)
                label_match_percentage = (label_match / total_rows) * 100 if total_rows > 0 else 0
                aka_match_percentage = (aka_match / total_rows) * 100 if total_rows > 0 else 0

                # Store the results for this JSONL file
                results[base_name] = {
                    "label_match_percentage": label_match_percentage,
                    "aka_match_percentage": aka_match_percentage
                }

    # Save the results to the output JSON file
    with open(output_file, 'w', encoding='utf-8') as output:
        json.dump(results, output, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process JSONL files and match against Excel data.")
    parser.add_argument("root_folder", help="Root folder containing JSONL files.")
    parser.add_argument("excel_file", help="Excel file with multiple sheets.")
    parser.add_argument("output_file", help="Output JSON file to store results.")

    args = parser.parse_args()

    # Call the function with provided arguments
    process_files(args.root_folder, args.excel_file, args.output_file)
