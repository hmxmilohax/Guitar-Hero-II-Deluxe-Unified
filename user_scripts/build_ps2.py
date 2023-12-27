import sys
sys.path.append("../dependencies/dev_scripts")

from build_ark import build_patch_ark
from download_mackiloha import download_mackiloha

successful_extraction = download_mackiloha()

if successful_extraction:
    build_patch_ark(False, rpcs3_mode=False)
    print("PS2 ARK built successfully.")
    print("You may find the files needed to build an ISO in /_build/ps2/.")
else:
    print("Failed to extract Mackiloha-suite-archive.zip. Please check the download and extraction process.")
