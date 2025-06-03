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
        file_name = Path(input["file_name"]).resolve()
        components: Dict[str, bool] = {}

        try:
            source_code = file_name.read_text(encoding="utf-8")
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
                compile(source_code, str(file_name), "exec")
                components["can_compile"] = True
            except Exception:
                components["can_compile"] = False
                return self._final_score(components)

            try:
                py_compile.compile(str(file_name), doraise=True)
                components["py_compile_ok"] = True
            except Exception:
                components["py_compile_ok"] = False
                return self._final_score(components)

            try:
                spec = importlib.util.spec_from_file_location("mod", str(file_name))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore
                components["can_import"] = True
            except Exception:
                components["can_import"] = False
                return self._final_score(components)

        # Optional tool checks
        available = {tool._config.name: tool for tool in getattr(self, "tool_providers", [])}

        def safe_check(name: str, callback) -> bool:
            try:
                return callback()
            except Exception:
                return False

        components["formatter_idempotent"] = safe_check("black", lambda: (
            json.loads(available["black"].run({"target": str(file_name), "check": True}, session_id=self._session_id))["return_code"] == 0
        ))

        components["symbol_graph_valid"] = safe_check("symbol_graph", lambda: (
            lambda res: bool(res) and all(node.get("name") and node.get("lineno") for node in res.values())
        )(json.loads(available["symbol_graph"].run({"target": str(file_name)}, session_id=self._session_id))))

        components["mypy_ok"] = safe_check("mypy", lambda: (
            json.loads(available["mypy"].run({"target": str(file_name)}, session_id=self._session_id))["return_code"] in (0, 1)
        ))

        return self._final_score(components)

    def _final_score(self, components: Dict[str, bool]) -> ScoreOutputSchema:
        weights = {
            "utf8_valid": 0.15,
            "syntax_ok": 0.15,
            "can_compile": 0.15,
            "py_compile_ok": 0.10,
            "can_import": 0.10,
            "formatter_idempotent": 0.15,
            "symbol_graph_valid": 0.10,
            "mypy_ok": 0.10
        }

        # Compute weighted score
        score = round(
            sum(weights[k] for k, v in components.items() if v and k in weights),
            3
        )

        # Apply pass/fail threshold
        threshold = 0.85
        summary = (
            "✅ All critical checks passed." if score >= threshold
            else f"❌ Below threshold ({threshold}): " +
                ", ".join(k for k, v in components.items() if not v)
        )

        return ScoreOutputSchema(
            name=SCORING_METRIC_TYPE.CODE_STABILITY_SCORE,
            value=score,
            components={k: float(v) for k, v in components.items()},
            summary=summary
        )

