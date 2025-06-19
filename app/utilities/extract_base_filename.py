from pathlib import Path
import re


def extract_base_filename(path: Path | str) -> str:
    path = Path(path)  # 🔄 Normalize input
    name = path.stem
    # Strip known suffixes like __state_12345
    return re.sub(r"(__state_|__ctrl_|__sys_|__prog_)\d{10}$", "", name)