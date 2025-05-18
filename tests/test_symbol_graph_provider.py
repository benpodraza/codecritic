import unittest
from pathlib import Path
import tempfile

from app.extensions.context_providers.symbol_graph_provider import SymbolGraphProvider


class SymbolGraphProviderTests(unittest.TestCase):
    def test_missing_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            provider = SymbolGraphProvider(str(Path(tmp) / "missing.py"))
            self.assertEqual(provider.get_context(), {})

    def test_symbol_graph_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "mod.py"
            src.write_text(
                """import math as m
VAR = 1

def foo(x):
    return x + VAR

class Bar:
    def baz(self, y):
        return foo(y) + m.sqrt(y)
""",
                encoding="utf-8",
            )
            provider = SymbolGraphProvider(str(src))
            ctx = provider.get_context()
            graph = ctx["symbol_graph"]
            self.assertIn("mod.foo", graph)
            self.assertEqual(graph["mod.foo"]["type"], "function")
            self.assertIn("mod.Bar.baz", graph)
            self.assertEqual(
                set(graph["mod.Bar.baz"].get("calls", [])), {"foo", "sqrt"}
            )
            resolved = provider.resolve_symbol("mod.foo")
            self.assertIs(resolved, graph["mod.foo"])

    def test_package_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "pkg"
            pkg.mkdir()
            (pkg / "__init__.py").write_text("", encoding="utf-8")
            (pkg / "mod.py").write_text("def func():\n    pass\n", encoding="utf-8")
            provider = SymbolGraphProvider(str(pkg))
            ctx = provider.get_context()
            graph = ctx["symbol_graph"]
            self.assertIn("mod.func", graph)


if __name__ == "__main__":
    unittest.main()
