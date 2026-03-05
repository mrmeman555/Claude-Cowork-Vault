import PyPDF2
import os

folder = "/home/aaron/Projects/Working0/Active/Sprint_NetPlus/Phase_1_Roadmapping/Materials/Cengage_Materials/Extracted/Appendices"
files = ["Appendix_B_Subnets.pdf", "Appendix_C_Practice_Exam.pdf", "Appendix_D_Rubric.pdf"]

def extract_intro(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            # Read first 2 pages
            for i in range(min(2, len(reader.pages))):
                text += reader.pages[i].extract_text() + "\n"
            return text
    except Exception as e:
        return str(e)

for filename in files:
    path = os.path.join(folder, filename)
    print(f"--- {filename} ---")
    print(extract_intro(path)[:1000]) # Print first 1000 chars
    print("\n")
