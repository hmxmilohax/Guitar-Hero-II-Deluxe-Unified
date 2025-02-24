import os
import subprocess

def find_and_format_dta_files():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for root, _, files in os.walk(script_dir):
        dta_files = [file for file in files if file.endswith(".dta")]
        for dta_file in dta_files:
            print(f"Running arson-fmt on: {dta_file} in {root}")
            subprocess.run(f"/Users/jnack/Documents/GitHub/arson/target/debug/arson-fmt {dta_file}", shell=True, cwd=root)

if __name__ == "__main__":
    find_and_format_dta_files()