import os
import subprocess

# Ranges derived from TOC analysis
# Format: (Chapter_Num, Start_Page, End_Page)
# Note: End_Page is inclusive in our slice_pdf.py script
RANGES = [
    (1, 53, 71),
    (2, 107, 125),
    (3, 174, 188),
    (4, 232, 247),
    (5, 290, 307),
    (6, 351, 366),
    (7, 415, 432),
    (8, 474, 498),
    (9, 546, 561),
    (10, 597, 612),
    (11, 649, 663),
    (12, 706, 723),
]

SLICER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slice_pdf.py")
VENV_PYTHON = "/home/aaron/Projects/Working0/.venv/bin/python3"

def extract_all():
    for chap, start, end in RANGES:
        name = f"Chapter_{chap}_Review"
        range_str = f"{start}-{end}"
        
        print(f"📦 Extracting {name} (Pages {range_str})...")
        
        cmd = [VENV_PYTHON, SLICER_SCRIPT, range_str, name]
        
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            print(f"❌ Failed to extract {name}")

if __name__ == "__main__":
    extract_all()
