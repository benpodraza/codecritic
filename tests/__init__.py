import sys, types
from pathlib import Path

# Minimal stub for jinja2
class _Template:
    def __init__(self, text):
        self.text = text
    def render(self, **kwargs):
        return self.text
class _Loader:
    def __init__(self, path):
        self.path = Path(path)
class _Env:
    def __init__(self, loader):
        self.loader = loader
    def get_template(self, name):
        return _Template((self.loader.path / name).read_text())

sys.modules.setdefault('jinja2', types.SimpleNamespace(Environment=_Env, FileSystemLoader=_Loader, Template=_Template))

# Stub pytest to avoid import errors
sys.modules.setdefault('pytest', types.ModuleType('pytest'))

# Stub radon for tool runner imports
sys.modules.setdefault('radon', types.ModuleType('radon'))
sys.modules.setdefault('radon.complexity', types.SimpleNamespace(cc_visit=lambda code: []))
