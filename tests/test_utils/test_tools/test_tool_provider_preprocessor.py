import pytest
from app.systems.preprocessing.utils.tool_provider_preprocessor import ToolProviderPreprocessor
from app.utils.tools.tool_result import ToolResult

sample_code = "def add(x,y):return x+y"

def test_run_all_tools_success():
    provider = ToolProviderPreprocessor()
    results = provider.run_all(sample_code)

    assert "black" in results
    assert "ruff" in results
    assert "docformatter" in results
    assert "mypy" in results
    assert "radon" in results
    assert all(res.status == "success" for res in results.values())

def test_quality_score_computes_score():
    provider = ToolProviderPreprocessor()
    result = provider.get_quality_score(sample_code)

    assert "score" in result
    assert 0.0 <= result["score"] <= 1.0
    assert "tools" in result

def test_ruff_output_triggers_deduction(monkeypatch):
    """Covers line 56: if 'error' in results['ruff'].output.lower()"""

    # Patch run_tool to inject 'error' string into ruff output
    def fake_run_tool(name, code):
        if name == "ruff":
            return ToolResult(name, "success", "some ERROR found", {"length": 123})
        else:
            return ToolResult(name, "success", "ok", {"length": 1})

    provider = ToolProviderPreprocessor()
    monkeypatch.setattr(provider, "run_tool", fake_run_tool)

    score = provider.get_quality_score("x = 1")
    assert score["score"] < 1.0
    assert "ruff" in score["tools"]

def test_list_tools_returns_registered_names():
    """Covers line 66: list_tools implementation"""
    provider = ToolProviderPreprocessor()
    tools = provider.list_tools()
    assert isinstance(tools, dict)
    assert "ruff" in tools
    assert "black" in tools