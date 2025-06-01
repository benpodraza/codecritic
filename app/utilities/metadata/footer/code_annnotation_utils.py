from __future__ import annotations
from typing import Tuple

FOOTER_START = "# --- Agent Notes"
FOOTER_END = "# -----------------------------------------------"

def strip_agent_notes(file_content: str) -> str:
    """Remove the agent notes footer from the file (if present)."""
    lines = file_content.strip().splitlines()
    start_idx = None

    for i, line in enumerate(lines):
        if line.strip().startswith(FOOTER_START):
            start_idx = i
            break

    return "\n".join(lines[:start_idx]) if start_idx is not None else file_content.strip()


def append_agent_note(file_content: str, system: str, agent_name: str, note: str) -> str:
    """Append a new agent note to the bottom of the file."""
    base = strip_agent_notes(file_content)

    formatted_note = (
        f"{FOOTER_START} ({system} / {agent_name}) ---\n" +
        "\n".join(f"# {line.strip()}" for line in note.strip().splitlines()) +
        f"\n{FOOTER_END}"
    )

    return base.rstrip() + "\n\n" + formatted_note


def split_code_and_notes(file_content: str) -> Tuple[str, str]:
    """Return (raw_code, extracted_footer_notes) without modifying whitespace"""
    lines = file_content.splitlines()  # No .strip() here
    start_idx = None

    for i, line in enumerate(lines):
        if line.strip().startswith(FOOTER_START):  # You may keep this .strip() for detecting footer
            start_idx = i
            break

    if start_idx is not None:
        code_part = "\n".join(lines[:start_idx])  # No .strip() here to preserve whitespace
        notes_part = "\n".join(lines[start_idx:])
        return code_part, notes_part

    return file_content, ""  
