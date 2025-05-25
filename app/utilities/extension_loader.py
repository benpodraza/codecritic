from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from typing import Type

def import_class_from_extension(artifact_path: str | Path, base_cls: Type) -> Type:
    file_path = Path("extensions") / f"{artifact_path}.py"
    if not file_path.exists():
        raise FileNotFoundError(f"Extension file not found: {file_path}")

    spec = spec_from_file_location("dynamic_module", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load: {file_path}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    for attr in module.__dict__.values():
        if isinstance(attr, type) and issubclass(attr, base_cls) and attr is not base_cls:
            return attr

    raise ImportError(f"No subclass of {base_cls.__name__} found in: {file_path}")
