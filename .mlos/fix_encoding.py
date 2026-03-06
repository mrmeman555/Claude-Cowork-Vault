#!/usr/bin/env python3
"""Fix UTF-8 mojibake in vault files caused by Windows stdin encoding."""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
VAULT = ROOT / "vault"

# Common UTF-8 mojibake patterns (UTF-8 bytes decoded as Latin-1/cp1252)
REPLACEMENTS = {
    "\u00e2\u0080\u0094": "\u2014",  # em-dash
    "\u00e2\u0080\u0093": "\u2013",  # en-dash
    "\u00e2\u0080\u0099": "\u2019",  # right single quote
    "\u00e2\u0080\u0098": "\u2018",  # left single quote
    "\u00e2\u0080\u009c": "\u201c",  # left double quote
    "\u00e2\u0080\u009d": "\u201d",  # right double quote
    "\u00e2\u0086\u0094": "\u2194",  # left-right arrow
    "\u00e2\u0086\u0092": "\u2192",  # right arrow
    "\u00c2\u00a7": "\u00a7",        # section sign
}

fixed = 0
for f in VAULT.rglob("*.md"):
    content = f.read_text(encoding="utf-8")
    original = content
    for bad, good in REPLACEMENTS.items():
        content = content.replace(bad, good)
    if content != original:
        f.write_text(content, encoding="utf-8")
        print(f"  Fixed: {f.relative_to(ROOT)}")
        fixed += 1
    else:
        print(f"  OK: {f.relative_to(ROOT)}")

print(f"\n  {fixed} file(s) fixed.")
