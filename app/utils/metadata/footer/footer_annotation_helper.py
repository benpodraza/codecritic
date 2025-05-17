"""
footer_annotation_helper.py

Provides tools to extract, reapply, and append AI-FIRST metadata footer annotations.

Used by all agent types when modifying source code during generation, review, or mediation.
"""

from typing import List

# === MARKER CONSTANT ===
FOOTER_HEADER = "# === AI-FIRST METADATA ==="


def strip_metadata_footer(code: str) -> tuple[str, List[str]]:
    """
    Remove all AI-FIRST METADATA footer blocks from a code string.

    Returns:
        (stripped_code, footer_lines)
    """
    lines = code.strip().splitlines()
    cutoff = len(lines)

    for i in reversed(range(len(lines))):
        if lines[i].startswith(FOOTER_HEADER):
            cutoff = i
        elif lines[i].startswith("#") and i > 0 and lines[i - 1].startswith(FOOTER_HEADER):
            continue
        else:
            break

    stripped = lines[:cutoff]
    footers = lines[cutoff:]
    return "\n".join(stripped).strip(), footers


def append_metadata_footer(code: str, metadata: dict) -> str:
    """
    Append a structured metadata footer block to the code.
    """
    footer_lines = [FOOTER_HEADER]
    for key, value in metadata.items():
        footer_lines.append(f"# {key}: {value}")
    return code.rstrip() + "\n\n" + "\n".join(footer_lines) + "\n"


def reapply_footer(code: str, previous_footer: List[str], new_footer: dict) -> str:
    """
    Reattach any prior footer, then append a new structured block.
    """
    code = code.strip()
    if previous_footer:
        code += "\n\n" + "\n".join(previous_footer)
    return append_metadata_footer(code, new_footer)
