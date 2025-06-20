from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from typing import Type, Union
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

def import_class_from_extension(
    artifact_path: Union[str, Path],
    base_cls: Type
) -> Type:
    """
    Dynamically load the first subclass of `base_cls` from an extension file.
    The file is resolved via the FileManager under FILETYPE.EXTENSION.
    """
    name     = str(artifact_path)
    rel_path = f"{name}.py"
    ftype    = FILETYPE.EXTENSION

    # Check existence via FileManager
    if not fm.exists(ftype, rel_path):
        raise FileNotFoundError(f"Extension file not found: {rel_path}")

    # Resolve to a real Path for the loader
    file_path = fm.resolve(ftype, rel_path)

    # Load module spec and execute
    spec = spec_from_file_location(name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load extension module: {file_path}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find and return the first subclass of base_cls
    for attr in module.__dict__.values():
        if isinstance(attr, type) and issubclass(attr, base_cls) and attr is not base_cls:
            return attr

    raise ImportError(f"No subclass of {base_cls.__name__} found in: {file_path}")
