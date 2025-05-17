import unittest
from importlib import import_module
from pathlib import Path
import sys

from app.factories.tool_provider import ToolProviderFactory


class ToolProviderTests(unittest.TestCase):
    def setUp(self):
        import_module("app.extensions.tool_providers")

    def test_black_provider(self):
        tmp = Path("tp_black.py")
        tmp.write_text("x=1")
        try:
            provider = ToolProviderFactory.create("black")
            result = provider.run(str(tmp))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.args[0], sys.executable)
            self.assertEqual(tmp.read_text(), "x = 1\n")
        finally:
            tmp.unlink(missing_ok=True)

    def test_mypy_provider(self):
        tmp = Path("tp_mypy.py")
        tmp.write_text("a: int = 1\n")
        try:
            provider = ToolProviderFactory.create("mypy")
            result = provider.run(str(tmp))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.args[0], sys.executable)
        finally:
            tmp.unlink(missing_ok=True)

    def test_ruff_provider(self):
        tmp = Path("tp_ruff.py")
        tmp.write_text("x = 1\n")
        try:
            provider = ToolProviderFactory.create("ruff")
            result = provider.run(str(tmp))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.args[0], sys.executable)
        finally:
            tmp.unlink(missing_ok=True)

    def test_radon_provider(self):
        tmp = Path("tp_radon.py")
        tmp.write_text("def f(x):\n    return x + 1\n")
        try:
            provider = ToolProviderFactory.create("radon")
            try:
                result = provider.run(str(tmp))
            except RuntimeError:
                self.skipTest("radon tool unavailable")
            else:
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.args[0], sys.executable)
        finally:
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
