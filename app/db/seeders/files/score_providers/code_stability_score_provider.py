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
        file_name = Path(input["file_path"]).resolve()
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

        return self._final_score(components)

    def _final_score(self, components: Dict[str, bool]) -> ScoreOutputSchema:
        critical_keys = ["utf8_valid", "syntax_ok", "can_compile", "py_compile_ok", "can_import"]
        passed = all(components.get(k, False) for k in critical_keys)
        value = 1.0 if passed else 0.0
        summary = "✅ Executable" if passed else "❌ Not executable"

        return ScoreOutputSchema(
            name=SCORING_METRIC_TYPE.CODE_STABILITY_SCORE,
            value=value,
            components={k: float(v) for k, v in components.items()},
            summary=summary
        )
