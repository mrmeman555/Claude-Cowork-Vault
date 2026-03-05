import os
from PyPDF2 import PdfReader

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(BASE_DIR, "NetPlusBook.pdf")

def list_bookmarks(outline, level=0):
    for item in outline:
        if isinstance(item, list):
            list_bookmarks(item, level + 1)
        else:
            try:
                # Get title and page number
                title = item.title
                page = -1
                if item.page:
                    # In newer PyPDF2, page retrieval can be indirect
                    # This is a best-effort to get the page index
                    page = reader.get_destination_page_number(item) + 1
                
                print(f"{'  ' * level}- {title} (Page {page})")
            except Exception as e:
                # Skip items that fail to resolve
                pass

if not os.path.exists(PDF_PATH):
    print(f"❌ PDF not found at {PDF_PATH}")
else:
    print(f"📖 Reading Table of Contents from: {PDF_PATH}")
    reader = PdfReader(PDF_PATH)
    list_bookmarks(reader.outline)
