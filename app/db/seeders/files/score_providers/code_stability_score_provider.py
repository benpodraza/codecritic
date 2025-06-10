import ast
import json
import py_compile
import importlib.util
from pathlib import Path
from typing import Dict
import contextlib
import sys
import io
import uuid

from app.providers.score_provider_base import ScoreProviderBase
from app.db.schemas import ScoreOutputSchema
from app.enums.scoring_enums import SCORING_METRIC_TYPE
from app.utilities.metadata.footer.code_annnotation_utils import split_code_and_notes

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
        original_path = Path(input["file_path"]).resolve()
        components: Dict[str, bool] = {}

        # Read raw code and verify UTF-8
        try:
            raw_code = original_path.read_text(encoding="utf-8")
            components["utf8_valid"] = True
        except Exception:
            components["utf8_valid"] = False
            return self._final_score(components)

        # Strip footer annotations without modifying actual code structure
        stripped_code, _ = split_code_and_notes(raw_code)

        # Always write a clean temp file with newline termination
        safe_path = Path("working_files") / f"{uuid.uuid4().hex}_stripped.py"
        safe_path.write_text(stripped_code.rstrip() + "\n", encoding="utf-8")

        # Reload stripped_code from disk to ensure parity with lint input
        stripped_code = safe_path.read_text(encoding="utf-8")

        with suppress_output():
            # Syntax and compile check
            try:
                compile(stripped_code, str(safe_path), "exec")
                ast.parse(stripped_code)
                components["syntax_ok"] = True
            except (SyntaxError, IndentationError):
                components["syntax_ok"] = False
                return self._final_score(components)

            # py_compile
            try:
                py_compile.compile(str(safe_path), doraise=True)
                components["py_compile_ok"] = True
            except Exception:
                components["py_compile_ok"] = False
                return self._final_score(components)

            # Import stripped code
            try:
                spec = importlib.util.spec_from_file_location("mod", str(safe_path))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore
                components["can_import"] = True
            except Exception:
                components["can_import"] = False
                return self._final_score(components)

        # Special check for Ruff parse error
        ruff_parse_error = "Failed to parse" in stripped_code
        components["ruff_parse_error"] = not ruff_parse_error
        if ruff_parse_error:
            return self._final_score(components)

        return self._final_score(components)

    def _final_score(self, components: Dict[str, bool]) -> ScoreOutputSchema:
        critical_keys = ["utf8_valid", "syntax_ok", "py_compile_ok", "can_import", "ruff_parse_error"]
        passed = all(components.get(k, False) for k in critical_keys)
        value = 1.0 if passed else 0.0
        summary = "✅ Executable" if passed else "❌ Not executable"

        return ScoreOutputSchema(
            name=SCORING_METRIC_TYPE.CODE_STABILITY_SCORE,
            value=value,
            components={k: float(v) for k, v in components.items()},
            summary=summary
        )
