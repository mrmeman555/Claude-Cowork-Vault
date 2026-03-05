import PyPDF2
import re
import sys

def extract_objectives(pdf_path):
    objectives = []
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Pattern to find objectives: 1.1 Explain... or 2.3 Configure...
            # This regex looks for a digit, a dot, a digit, a space, and then the rest of the line
            # It captures: ID (e.g. 1.1) and Title (e.g. Explain the OSI Model)
            pattern = re.compile(r'^(\d+\.\d+)\s+(.*)$', re.MULTILINE)
            
            matches = pattern.findall(text)
            
            current_domain = "0.0"
            
            for match in matches:
                obj_id = match[0]
                title = match[1].strip()
                
                # Determine Domain based on the first digit of the ID
                domain_num = obj_id.split('.')[0]
                
                # Simple heuristic to extract the first word as the verb
                # We might need to refine this if the verb isn't always the first word
                verb = title.split(' ')[0]
                
                objectives.append({
                    "id": obj_id,
                    "title": title,
                    "verb": verb,
                    "domain": domain_num
                })
                
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return []

    return objectives

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_objectives.py <pdf_path>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    objs = extract_objectives(pdf_path)
    
    print(f"Found {len(objs)} objectives.")
    
    # Print in Markdown Table format for easy copy-paste or further processing
    current_domain = "0"
    for obj in objs:
        if obj['domain'] != current_domain:
            current_domain = obj['domain']
            print(f"\n### Domain {current_domain}.0")
            print("| Objective ID | Objective Title | Command Verb | Cognitive Level | Notes |")
            print("|---|---|---|---|---|")
            
        print(f"| {obj['id']} | {obj['title']} | {obj['verb']} | TBD | |")
