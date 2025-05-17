"""
builtin_tool_loader: Registers built-in tools with the global ToolRegistry.
"""

from app.utils.tools.tool_registry import ToolRegistry
from app.utils.tools.tool_runners.black_runner import run_black
from app.utils.tools.tool_runners.ruff_runner import run_ruff
from app.utils.tools.tool_runners.docformatter_runner import run_docformatter
from app.utils.tools.tool_runners.mypy_runner import run_mypy
from app.utils.tools.tool_runners.radon_runner import run_radon
from app.utils.tools.tool_runners.sonarcloud_runner import run_sonarcloud


def load_builtin_tools(registry: ToolRegistry):
    registry.register("black", run_black)
    registry.register("ruff", run_ruff)
    registry.register("docformatter", run_docformatter)
    registry.register("mypy", run_mypy)
    registry.register("radon", run_radon)
    registry.register("sonarcloud", run_sonarcloud)
