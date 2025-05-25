from app.providers.context_provider_base import ContextProviderBase
import json

class BasicContextProvider(ContextProviderBase):
    def _run(self, input: dict) -> str:
        return json.dumps({
            "file_path": "tests/example.py",
            "source_code": "def example():\n    pass\n"
        })
