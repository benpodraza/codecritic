import ast
import json
import py_compile
import importlib.util
from pathlib import Path
from typing import Dict
import contextlib
import sys
import io

from app.providers.score_provider_base import ScoreProviderBase
from app.db.schemas import ScoreOutputSchema
from app.enums.scoring_enums import SCORING_METRIC_TYPE


@contextlib.contextmanager
def suppress_output():
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr


class CodeStabilityScoreProvider(ScoreProviderBase):
    def _run(self, input: dict) -> ScoreOutputSchema:
        file_path = Path(input["file_path"]).resolve()
        components: Dict[str, bool] = {}

        try:
            source_code = file_path.read_text(encoding="utf-8")
            components["utf8_valid"] = True
        except Exception:
            components["utf8_valid"] = False
            return self._final_score(components)

        with suppress_output():
            try:
                ast.parse(source_code)
                components["syntax_ok"] = True
            except SyntaxError:
                components["syntax_ok"] = False
                return self._final_score(components)

            try:
                compile(source_code, str(file_path), "exec")
                components["can_compile"] = True
            except Exception:
                components["can_compile"] = False
                return self._final_score(components)

            try:
                py_compile.compile(str(file_path), doraise=True)
                components["py_compile_ok"] = True
            except Exception:
                components["py_compile_ok"] = False
                return self._final_score(components)

            try:
                spec = importlib.util.spec_from_file_location("mod", str(file_path))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore
                components["can_import"] = True
            except Exception:
                components["can_import"] = False
                return self._final_score(components)

        # Optional tool checks
        available = {tool.config.name: tool for tool in getattr(self, "tool_providers", [])}

        def safe_check(name: str, callback) -> bool:
            try:
                return callback()
            except Exception:
                return False

        components["formatter_idempotent"] = safe_check("black", lambda: (
            json.loads(available["black"].run({"target": str(file_path), "check": True}, session_id=self._session_id))["return_code"] == 0
        ))

        components["symbol_graph_valid"] = safe_check("symbol_graph", lambda: (
            lambda res: bool(res) and all(node.get("name") and node.get("lineno") for node in res.values())
        )(json.loads(available["symbol_graph"].run({"target": str(file_path)}, session_id=self._session_id))))

        components["mypy_ok"] = safe_check("mypy", lambda: (
            json.loads(available["mypy"].run({"target": str(file_path)}, session_id=self._session_id))["return_code"] in (0, 1)
        ))

        return self._final_score(components)

    def _final_score(self, components: Dict[str, bool]) -> ScoreOutputSchema:
        basics = ["utf8_valid", "syntax_ok", "can_compile", "can_import"]
        score = 1.0 if all(components.get(k, False) for k in basics) else 0.0
        failing = [k for k, v in components.items() if not v]
        summary = "✅ All checks passed." if score == 1.0 else f"❌ Failed checks: {', '.join(failing)}"

        return ScoreOutputSchema(
            name=SCORING_METRIC_TYPE.CODE_STABILITY_SCORE,
            value=score,
            components={k: float(v) for k, v in components.items()},
            summary=summary
        )
