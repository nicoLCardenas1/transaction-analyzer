
import os


def read_transaction_file(file_path):
   
    if not os.path.exists(file_path):
        print(f"Error - transaction file '{file_path}' was not found.")
        return []

    if not os.path.isfile(file_path):
         print(f"Error: '{file_path}' is not a file.")
         return []


# "r" means read and as f is an alias 
# 
    try:
         with open(file_path, "r", encoding="utf-8") as f:
             raw_lines = f.readlines()
    except OSError as e:
         print(f"Error - could not read transaction file '{file_path}' ({e}).")
         return []

    if not raw_lines:
         print(f"Warning: transaction file '{file_path}' is empty.")
         return []

    records = []
    for line_number, raw_line in enumerate(raw_lines, start=1):
        line = raw_line.rstrip("\n").rstrip("\r")
        if line.strip() == "":
            continue  # skip blank lines instead of treating them as invalid records
        fields = line.split("|")
        records.append((line_number, fields))

    return records
