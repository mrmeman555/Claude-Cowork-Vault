import os
import argparse
from PyPDF2 import PdfReader, PdfWriter

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(BASE_DIR, "NetPlusBook.pdf")
OUTPUT_DIR = os.path.join(BASE_DIR, "Extracted")

def slice_pdf(start_page, end_page, output_name):
    """Extract a range of pages from the source PDF."""
    
    if not os.path.exists(PDF_PATH):
        print(f"❌ Source PDF not found at: {PDF_PATH}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    reader = PdfReader(PDF_PATH)
    writer = PdfWriter()

    # Adjust for 0-based index
    start_idx = start_page - 1
    end_idx = end_page  # Slice is exclusive at the end, but we want inclusive for user

    # Validate bounds
    total_pages = len(reader.pages)
    if start_idx < 0 or end_idx > total_pages:
        print(f"❌ Invalid page range. PDF has {total_pages} pages.")
        return

    print(f"✂️  Slicing pages {start_page} to {end_page}...")

    for i in range(start_idx, end_idx):
        writer.add_page(reader.pages[i])

    output_filename = f"{output_name}.pdf"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"✅ Saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Extract pages from Cengage Net+ Book")
    parser.add_argument("range", help="Page range (e.g., 50-65)")
    parser.add_argument("name", help="Output filename (without extension)")
    
    args = parser.parse_args()

    try:
        if '-' in args.range:
            start, end = map(int, args.range.split('-'))
        else:
            start = int(args.range)
            end = start
            
        slice_pdf(start, end, args.name)
        
    except ValueError:
        print("❌ Invalid range format. Use 'Start-End' (e.g., 50-65)")

if __name__ == "__main__":
    main()
