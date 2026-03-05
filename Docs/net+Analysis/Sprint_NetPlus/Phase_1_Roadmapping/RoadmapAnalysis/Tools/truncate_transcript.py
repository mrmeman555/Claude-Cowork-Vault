import os

target_file = "/home/aaron/Projects/Working0/Active/Sprint_NetPlus/Phase_1_Roadmapping/Materials/Gemini_Logos_Transcript.md"
search_string = "Hm.. I'm not sure about sharing the actual prompts.."

if not os.path.exists(target_file):
    print(f"Error: File not found at {target_file}")
    exit(1)

with open(target_file, "r") as f:
    lines = f.readlines()

cut_index = -1
for i, line in enumerate(lines):
    if search_string in line:
        cut_index = i
        break

if cut_index != -1:
    print(f"Found search string at line {cut_index + 1}. Truncating file...")
    new_content = lines[:cut_index]
    with open(target_file, "w") as f:
        f.writelines(new_content)
    print("File truncated successfully.")
else:
    print(f"Search string '{search_string}' not found in file.")
