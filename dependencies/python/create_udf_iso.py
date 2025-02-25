#!/usr/bin/env python3

import os
import sys
import pycdlib

def add_directory_to_iso(iso_obj, source_dir, iso_path="/"):
    for entry in os.scandir(source_dir):
        entry_name = entry.name
        source_path = os.path.join(source_dir, entry_name)
        iso_entry_path = f"{iso_path}{entry_name.upper()}"

        if entry.is_dir():
            iso_obj.add_directory(iso_entry_path, rr_name=entry_name)
            add_directory_to_iso(iso_obj, source_path, iso_entry_path + "/")
        else:
            iso_obj.add_file(source_path, iso_entry_path + ";1", rr_name=entry_name)

def create_udf_iso(input_folder, output_filename):
    iso = pycdlib.PyCdlib()
    # Use UDF 2.60 here (the only option in newer pycdlib versions)
    iso.new(
        interchange_level=4,
        rock_ridge='1.10',
        udf='1.02',
        vol_ident='UDF_VOL'
    )
    add_directory_to_iso(iso, input_folder)
    iso.write(output_filename)
    iso.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_udf_iso.py <input_folder> [output.iso]")
        sys.exit(1)

    input_folder = sys.argv[1]
    if not os.path.isdir(input_folder):
        print(f"Error: {input_folder} is not a valid directory.")
        sys.exit(1)

    output_iso = "output.iso"
    if len(sys.argv) > 2:
        output_iso = sys.argv[2]

    create_udf_iso(input_folder, output_iso)
    print(f"Created UDF ISO image -> {output_iso}")

if __name__ == "__main__":
    main()
