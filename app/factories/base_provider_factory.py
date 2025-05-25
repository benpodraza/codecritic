from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from app.db.connection import DB_PATH
from app.providers.base_provider import BaseProvider


class BaseProviderFactory:
    config_model = None  
    base_class = BaseProvider  

    @classmethod
    def create(cls, id: int, **kwargs):
        # Step 1: Load config from DB
        engine = create_engine(f"sqlite:///{DB_PATH}")
        with Session(bind=engine) as session:
            config = session.get(cls.config_model, id)
            if not config:
                raise ValueError(f"{cls.config_model.__name__} ID {id} not found")

        # Step 2: Load extension
        ext_path = Path("extensions") / f"{config.artifact_path}.py"
        if not ext_path.exists():
            raise FileNotFoundError(f"Extension not found: {ext_path}")

        spec = spec_from_file_location("provider_extension", ext_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        provider_class = None
        for obj in module.__dict__.values():
            if isinstance(obj, type) and issubclass(obj, cls.base_class) and obj is not cls.base_class:
                provider_class = obj
                break

        if not provider_class:
            raise ImportError(f"No valid subclass of {cls.base_class.__name__} found in {ext_path}")

        # Step 3: Instantiate and wire dependencies
        instance = provider_class(config=config)
        instance.resolve_dependencies(**kwargs)
        return instance
