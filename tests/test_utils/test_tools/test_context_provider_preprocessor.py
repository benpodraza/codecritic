import tempfile
from unittest.mock import Mock
import pytest
from pathlib import Path
from app.systems.preprocessing.utils.context_provider_preprocessor import ContextProviderPreprocessor
from app.utils.symbol_graph.symbol_service import SymbolService


def test_build_context_structure():
    root = Path("tests/data/test_context_provider_preprocessor")
    symbol_file = root / "example.py"

    symbol_service = SymbolService(root_path=root)
    provider = ContextProviderPreprocessor(symbol_service)

    context = provider.get_context({
        "symbol": "my_symbol",
        "file": str(symbol_file)
    })

    assert context["symbol"] == "my_symbol"
    assert context["source_file"].endswith("example.py")
    assert isinstance(context["children"], list)
    assert context["breadcrumbs"] == 0
    assert context["logger_calls"] == 1
    assert context["symbol_info"]["name"] == "my_symbol"
    assert isinstance(context["resolved_imports"], dict)


def test_metadata_footer_skips_header_line(tmp_path):
    file = tmp_path / "header_only.py"
    file.write_text("""#  === AI-FIRST METADATA ===
#  something: value
#  === AI-FIRST METADATA ===
#  another: value
""")

    symbol_service = SymbolService(root_path=tmp_path)
    provider = ContextProviderPreprocessor(symbol_service)
    meta = provider._extract_metadata_footer(file)
    assert "something" in meta
    assert "another" in meta


def test_extract_metadata_footer_continues_on_marker(tmp_path):
    file = tmp_path / "meta_test.py"
    file.write_text("""#  === AI-FIRST METADATA ===
#  annotations_added: test
#  === AI-FIRST METADATA ===
#  modifications: example
""")

    symbol_service = SymbolService(root_path=tmp_path)
    provider = ContextProviderPreprocessor(symbol_service)
    meta = provider._extract_metadata_footer(file)

    assert meta["annotations_added"] == "test"
    assert meta["modifications"] == "example"


def test_extract_metadata_footer_skips_header_and_reads_kv(tmp_path):
    file = tmp_path / "meta_headers.py"
    file.write_text("""#  === AI-FIRST METADATA ===
#  annotations_added: test_value
#  random_header: skipped
""")

    symbol_service = SymbolService(root_path=tmp_path)
    provider = ContextProviderPreprocessor(symbol_service)
    meta = provider._extract_metadata_footer(file)
    assert meta["annotations_added"] == "test_value"
    assert "random_header" in meta


def test_resolve_imports_partial_parse(tmp_path):
    file = tmp_path / "partial_imports.py"
    file.write_text("""from invalid.module import something
from math import sqrt
""")

    symbol_service = SymbolService(root_path=tmp_path)
    provider = ContextProviderPreprocessor(symbol_service)
    resolved = provider._resolve_imports(file)

    assert isinstance(resolved, dict)
    assert "sqrt" in resolved or resolved == {}
    assert "something" not in resolved


def test_resolve_imports_success(tmp_path):
    file = tmp_path / "imports.py"
    file.write_text("from math import sqrt\n")

    symbol_service = SymbolService(root_path=tmp_path)
    provider = ContextProviderPreprocessor(symbol_service)
    resolved = provider._resolve_imports(file)

    assert isinstance(resolved, dict)
    assert "sqrt" in resolved or resolved == {}


def test_resolve_imports_failure_path(tmp_path):
    file = tmp_path / "bad_imports.py"
    file.write_text("from made.up.module import MissingClass\n")

    symbol_service = SymbolService(root_path=tmp_path)
    provider = ContextProviderPreprocessor(symbol_service)
    resolved = provider._resolve_imports(file)

    assert isinstance(resolved, dict)
    assert "MissingClass" not in resolved


def test_resolve_imports_with_nonmatching_from_syntax(tmp_path):
    file = tmp_path / "fail_parse.py"
    file.write_text("""from !@#invalid import ???
""")

    symbol_service = SymbolService(root_path=tmp_path)
    provider = ContextProviderPreprocessor(symbol_service)
    resolved = provider._resolve_imports(file)

    assert isinstance(resolved, dict)
    assert resolved == {}


def test_resolve_imports_simulate_file_resolution_failure(tmp_path):
    file = tmp_path / "edge_case_import.py"
    file.write_text(
"""
from x.y.z.fake1 import A
from x.y.z.fake2 import B
from x.y.z.fake3 import C
from x.y.z.fake4 import D
from x.y.z.fake5 import E
"""
)

    symbol_service = SymbolService(root_path=tmp_path)
    provider = ContextProviderPreprocessor(symbol_service)
    resolved = provider._resolve_imports(file)

    assert isinstance(resolved, dict)
    assert resolved == {}
    assert all(symbol not in resolved for symbol in ["A", "B", "C", "D", "E"])


def test_resolve_imports_module_file_found(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    module_file = tmp_path / "mymodule.py"
    module_file.write_text("class Foo: pass\n")
    test_file = tmp_path / "test.py"
    test_file.write_text("from mymodule import Foo\n")

    symbol_service = SymbolService(root_path=tmp_path)
    provider = ContextProviderPreprocessor(symbol_service)
    resolved = provider._resolve_imports(test_file)

    assert "Foo" in resolved
    assert resolved["Foo"]["file"].endswith("mymodule.py")
    assert resolved["Foo"]["module_import_path"] == "mymodule.Foo"
    assert "class Foo" in resolved["Foo"]["source"]


def test_resolve_imports_read_text_exception(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    module_file = tmp_path / "badmodule.py"
    module_file.write_text("class Bar: pass\n")
    test_file = tmp_path / "test2.py"
    test_file.write_text("from badmodule import Bar\n")

    original_read_text = Path.read_text
    def fake_read_text(self, encoding="utf-8"):
        if self.name == "badmodule.py":
            raise IOError("read error")
        return original_read_text(self, encoding=encoding)
    monkeypatch.setattr(Path, "read_text", fake_read_text)

    symbol_service = SymbolService(root_path=tmp_path)
    provider = ContextProviderPreprocessor(symbol_service)
    resolved = provider._resolve_imports(test_file)

    assert resolved == {}

def test_extract_metadata_footer_hits_continue():
    # Prepare mock symbol_service (not used in this method but required for init)
    mock_symbol_service = Mock()

    # Create a temporary file with metadata footer
    content = """
Some code
# === AI-FIRST METADATA ===
# key: value
# === AI-FIRST METADATA ===
"""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    processor = ContextProviderPreprocessor(symbol_service=mock_symbol_service)
    result = processor._extract_metadata_footer(tmp_path)

    assert isinstance(result, dict)

    # Clean up
    tmp_path.unlink()