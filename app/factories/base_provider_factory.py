from sqlalchemy.orm import Session
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from app.db import init_db  # global DB engine instance
from app.providers.base_provider import BaseProvider
from app.enums.logging_enums import PROVIDER_TYPE, RunContext

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXTENSIONS_DIR = PROJECT_ROOT / "extensions"

engine = init_db(reset=False)


class BaseProviderFactory:
    config_model = None
    base_class = BaseProvider

    @classmethod
    def create(
        cls,
        id: int,
        *,
        context: RunContext,
        **kwargs
    ) -> BaseProvider:
        with Session(bind=engine) as session:
            config = session.get(cls.config_model, int(id))
            if not config:
                raise ValueError(f"{cls.config_model.__name__} ID {id} not found")

            ext_path = (EXTENSIONS_DIR / config.artifact_path).resolve()
            if not ext_path.exists():
                raise FileNotFoundError(f"Extension not found: {ext_path}")

        spec = spec_from_file_location(ext_path.stem, ext_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module spec for {ext_path}")

        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        provider_class = next(
            (obj for obj in vars(module).values()
             if isinstance(obj, type) and issubclass(obj, cls.base_class) and obj is not cls.base_class),
            None
        )

        if provider_class is None:
            raise ImportError(f"No valid subclass of {cls.base_class.__name__} found in {ext_path}")

        # 🎯 Extract and normalize config structure
        full_config = config.config or {}
        components = full_config.get("components") or {}
        params     = full_config.get("params") or {}

        # ✅ Create instance and attach structured config access
        instance = provider_class(config=config, context=context, **kwargs)
        instance._components = components
        instance._params = params

        return instance
