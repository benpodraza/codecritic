import ast
import uuid
from pathlib import Path
from typing import Tuple

FOOTER_START = "# --- Agent Notes"
FOOTER_END = "# -----------------------------------------------"

def split_content_and_notes(file_content: str) -> Tuple[str, str]:
    """Return (content_with_safe_footer_removed, extracted_notes), preserving syntax."""
    footer_start = None
    line_sep = "\r\n" if "\r\n" in file_content else "\n"
    lines = file_content.splitlines(keepends=True)

    for i, line in enumerate(lines):
        if line.lstrip().startswith(FOOTER_START):
            footer_start = i
            break

    if footer_start is not None:
        code_part = "".join(lines[:footer_start])
        notes_part = "".join(lines[footer_start:])

        try:
            ast.parse(code_part)
            return code_part, notes_part
        except SyntaxError:
            safe_footer = (
                f"{line_sep}{FOOTER_START} (removed safely)\n"
                f"pass  # [Agent notes stripped for syntax integrity]{line_sep}"
                f"{FOOTER_END}{line_sep}"
            )
            return code_part + safe_footer, notes_part

    return file_content, ""

def append_agent_note(file_content: str, system: str, agent_name: str, note: str) -> str:
    base, _ = split_content_and_notes(file_content)  # strip if possible, fallback-safe

    formatted_note = (
        f"{FOOTER_START} ({system} / {agent_name}) ---\n" +
        "".join(f"# {line}\n" for line in note.strip().splitlines()) +
        f"{FOOTER_END}\n"
    )

    return base.rstrip() + "\n\n" + formatted_note


# def prepare_file_for_linting(original_path: str) -> str:
#     original = Path(original_path)
#     raw = original.read_text(encoding="utf-8")

#     from .code_annnotation_utils import split_content_and_notes
#     code_part, _ = split_content_and_notes(raw)

#     try:
#         ast.parse(code_part)
#     except SyntaxError:
#         # Append safety pass to guarantee valid syntax
#         code_part += "\npass  # [Auto-patched for linting]\n"

#     temp_file = Path("working_files") / f"{uuid.uuid4().hex}_stripped.py"
#     temp_file.write_text(code_part.rstrip() + "\n", encoding="utf-8")

#     return str(temp_file)


