# Task: Build Sec+ Lab TOC/MOC

## What to do

Create a `Lab_TOC.md` file in `Sec+Analysis/` that inventories every Cengage Sec+ lab (.docx files).

## Where the labs are

Find all `.docx` lab files in the repo. They follow a naming pattern like `Lab04-2` (Module number - Lab number). Locate them and process every one.

## How to read each lab

Open each .docx file and extract:
1. **Lab ID** — from the filename (e.g., "Lab04-2")
2. **Lab Title** — the title/heading inside the document
3. **Stated Objective** — the purpose or learning objective stated at the top of the lab (usually the first paragraph or "Objectives" section). Keep it to 1-2 sentences.
4. **What you actually do** — brief summary of the hands-on actions (e.g., "Configure firewall ACLs in pfSense", "Analyze packet capture in Wireshark"). 1 sentence max.

## How to structure the output

Group labs by module number. For each module, include a table:

```markdown
## Module X — [Module Name if known]

| Lab ID | Title | Objective | Hands-On Action |
|--------|-------|-----------|-----------------|
| LabXX-1 | ... | ... | ... |
| LabXX-2 | ... | ... | ... |
```

At the bottom, include a summary:
- Total lab count
- Labs per module (count)
- Any modules with zero labs (flag these)

## Important notes

- Do NOT include full lab instructions or step-by-step procedures — just the metadata
- If a lab file can't be read or is corrupted, note it in the table as "[UNREADABLE]"
- If the lab's objective references specific exam objectives (like "1.4" or "SY0-701 Objective 2.5"), capture those in the Objective column
- Output file goes in: `Sec+Analysis/Lab_TOC.md`

## Context

This TOC will later be cross-referenced against the Cengage Appendix A (which maps every exam sub-item to a Bloom's Taxonomy level) to run the "Trap Lab Filter" — identifying which labs are worth doing vs. which are busy-work for topics that only need flashcard-level study.
