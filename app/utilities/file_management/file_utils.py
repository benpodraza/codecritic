from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import List, Optional
import shutil
import logging

# ─────────────────────────────────────────────
# 📂 File Types
# ─────────────────────────────────────────────

class FILETYPE(str, Enum):
    SEED_SOURCE = "seed_source"
    EXTENSION = "extension"
    INPUT = "input_file"
    WORKING = "working"
    SNAPSHOT = "snapshot"
    DATABASE = "database"
    TEMP = "temp"

# ─────────────────────────────────────────────
# 🗂️  File Path Roots
# ─────────────────────────────────────────────

FILE_PATHS = {
    FILETYPE.SEED_SOURCE: Path("app/db/seeders/files"),
    FILETYPE.EXTENSION: Path("extensions"),
    FILETYPE.WORKING: Path("working_files"),
    FILETYPE.SNAPSHOT: Path("experiments/snapshots"),
    FILETYPE.DATABASE: Path("experiments"),
    FILETYPE.INPUT: Path("."),
    FILETYPE.TEMP: Path("experiments/temp"),
}

# ─────────────────────────────────────────────
# 🧱 File Manager Interface
# ─────────────────────────────────────────────

class FileManagerBase(ABC):
    @abstractmethod
    def load(self, type: FILETYPE, filename: str) -> str: ...

    @abstractmethod
    def save(self, type: FILETYPE, filename: str, content: str) -> None: ...

    @abstractmethod
    def delete(self, type: FILETYPE, filename: str) -> None: ...

    @abstractmethod
    def copy(
        self,
        src_type: FILETYPE,
        src_filename: str,
        dst_type: FILETYPE,
        dst_filename: Optional[str] = None
    ) -> str: ...

    @abstractmethod
    def list_files(self, filetype: FILETYPE) -> list[str]: ...

    @abstractmethod
    def exists(self, type: FILETYPE, filename: str) -> bool:
        """Check if a file exists in the given file type location."""
        ...
    
    @abstractmethod
    def save_append(self, type: FILETYPE, filename: str, content: str) -> None:
        """
        Append content to an existing file, or create it if it does not exist.
        For blob storage, this should read + append + overwrite.
        """
        ...
    
    @abstractmethod
    def is_file(self, path: str) -> bool: ...
    
    @abstractmethod
    def is_dir(self, path: str) -> bool: ...

# ─────────────────────────────────────────────
# 💾 Local File System Implementation
# ─────────────────────────────────────────────

logger = logging.getLogger(__name__)

class LocalFileManager(FileManagerBase):
    def _resolve(self, type: FILETYPE, filename: str | Path) -> Path:
        if isinstance(filename, Path):
            filename = str(filename)
        if not filename or not isinstance(filename, str):
            raise ValueError("❌ filename must be a non-empty string")

        path = Path(filename)
        clean_name = path.name

        if type == FILETYPE.INPUT:
            resolved = (Path.cwd() / path).resolve()
            return resolved

        if type in {FILETYPE.SEED_SOURCE, FILETYPE.EXTENSION}:
            resolved = (FILE_PATHS[type] / path).resolve()
            return resolved

        resolved = (FILE_PATHS[type] / clean_name).resolve()
        return resolved

    def resolve_existing_filetype(self, filename: str) -> FILETYPE:
        candidate_name = Path(filename).name
        for ftype, base_path in FILE_PATHS.items():
            check_path = base_path / candidate_name
            if check_path.exists():
                return ftype
        raise FileNotFoundError(f"❌ File not found in any known FILE_PATHS: {candidate_name}")

    def load(self, type: FILETYPE, filename: str) -> str:
        path = self._resolve(type, filename)
        if not path.exists():
            raise FileNotFoundError(f"❌ File not found: {path}")
        content = path.read_text(encoding="utf-8")
        return content

    def save(self, type: FILETYPE, filename: str, content: str) -> None:
        path = self._resolve(type, filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def delete(self, type: FILETYPE, filename: str) -> None:
        try:
            path = self._resolve(type, filename)
            path.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"⚠️ Failed to delete {filename}: {e}")

    def copy(
        self,
        src_type: FILETYPE,
        src_filename: str,
        dst_type: FILETYPE,
        dst_filename: Optional[str] = None
    ) -> str:
        src_path = self._resolve(src_type, src_filename)
        dst_name = Path(dst_filename).name if dst_filename else Path(src_filename).name
        dst_path = self._resolve(dst_type, dst_name)

        if not src_path.exists():
            raise FileNotFoundError(f"❌ Source file not found: {src_path}")

        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src_path, dst_path)
        return str(dst_path)

    def list_files(self, filetype: FILETYPE) -> list[str]:
        base_path = FILE_PATHS[filetype]
        return [f.name for f in base_path.iterdir() if f.is_file()]
    
    def exists(self, type: FILETYPE, filename: str) -> bool:
        path = self._resolve(type, filename)
        return path.exists()
    
    def save_append(self, type: FILETYPE, filename: str, content: str) -> None:
        path = self._resolve(type, filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(content)

    def is_file(self, path: str) -> bool:
        return Path(path).is_file()

    def is_dir(self, path: str) -> bool:
        return Path(path).is_dir()

# ─────────────────────────────────────────────
# 🌍 Global Manager Registry
# ─────────────────────────────────────────────

_active_file_manager: FileManagerBase = LocalFileManager()

def get_file_manager() -> FileManagerBase:
    return _active_file_manager

def set_file_manager(manager: FileManagerBase):
    global _active_file_manager
    _active_file_manager = manager