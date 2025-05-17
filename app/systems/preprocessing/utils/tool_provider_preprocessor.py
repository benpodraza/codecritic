from app.utils.base_agent.tool_provider import ToolProvider
from app.utils.tools.tool_registry import ToolRegistry
from app.utils.tools.builtin_tool_loader import load_builtin_tools
from app.utils.tools.tool_result import ToolResult


class ToolProviderPreprocessor(ToolProvider):
    """
    ToolProvider for preprocessing agents.
    Wraps ToolRegistry and defines evaluation-level tool aggregations.
    """

    def __init__(self):
        self.registry = ToolRegistry()
        load_builtin_tools(self.registry)

    def run_tool(self, name: str, code: str) -> ToolResult:
        try:
            result = self.registry.run(name, code)
            return ToolResult(
                tool=name,
                status="success",
                output=result,
                metadata={"length": len(result)}
            )
        except Exception as e:
            return ToolResult(
                tool=name,
                status="error",
                output="",
                metadata={"error": str(e)}
            )

    def run_all(self, code: str) -> dict[str, ToolResult]:
        return {
            name: self.run_tool(name, code)
            for name in self.registry.list_tools()
        }

    def get_quality_score(self, code: str) -> dict:
        """
        Aggregates score-relevant tools and calculates a basic composite score.
        """
        results = {
            "pyrefactor": self.run_tool("pyrefactor", code),
            "ruff": self.run_tool("ruff", code),
            "mypy": self.run_tool("mypy", code),
        }

        score = 1.0
        deductions = 0.0

        if results["pyrefactor"].status == "error":
            deductions += 0.2

        if "error" in results["ruff"].output.lower():
            deductions += 0.1

        score -= deductions
        return {
            "score": round(max(0.0, score), 2),
            "tools": {k: v.output for k, v in results.items()}
        }

    def list_tools(self) -> dict[str, str]:
        return {
            name: "available" for name in self.registry.list_tools()
        }
