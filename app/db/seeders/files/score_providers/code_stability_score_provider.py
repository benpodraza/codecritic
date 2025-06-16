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

from pydantic import BaseModel

from app.enums.logging_enums import RunContext
from app.providers.score_provider_base import ScoreProviderBase
from app.db.schemas import CodeStabilityScoreConfig, ScoreOutputSchema, CodeStabilityScoreComponents
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
    ConfigSchema = CodeStabilityScoreConfig
    def _run(self, input: dict, context: RunContext | None = None) -> ScoreOutputSchema:
        original_path = Path(input["file_path"]).resolve()
        bool_components: Dict[str, bool] = {}

        # Read raw code and verify UTF-8
        try:
            raw_code = original_path.read_text(encoding="utf-8")
            bool_components["utf8_valid"] = True
        except Exception:
            bool_components["utf8_valid"] = False
            return self._final_score(bool_components)

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
                bool_components["syntax_ok"] = True
            except (SyntaxError, IndentationError):
                bool_components["syntax_ok"] = False
                return self._final_score(bool_components)

            # py_compile
            try:
                py_compile.compile(str(safe_path), doraise=True)
                bool_components["py_compile_ok"] = True
            except Exception:
                bool_components["py_compile_ok"] = False
                return self._final_score(bool_components)

            # Import stripped code
            try:
                spec = importlib.util.spec_from_file_location("mod", str(safe_path))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore
                bool_components["can_import"] = True
            except Exception:
                bool_components["can_import"] = False
                return self._final_score(bool_components)

        return self._final_score(bool_components)

    def _final_score(self, bool_components: Dict[str, bool]) -> ScoreOutputSchema:
        # 📦 Convert to float for schema compatibility
        components = CodeStabilityScoreComponents(
            type="code_stability", 
            utf8_valid=float(bool_components.get("utf8_valid", False)),
            syntax_ok=float(bool_components.get("syntax_ok", False)),
            py_compile_ok=float(bool_components.get("py_compile_ok", False)),
            can_import=float(bool_components.get("can_import", False))
        )
        # ✅ Overall score decision
        critical_keys = [
            components.utf8_valid,
            components.syntax_ok,
            components.py_compile_ok,
            components.can_import
        ]
        passed = all(v >= 1.0 for v in critical_keys)
        value = 1.0 if passed else 0.0
        summary = "✅ Executable" if passed else "❌ Not executable"

        return ScoreOutputSchema(
            name=SCORING_METRIC_TYPE.CODE_STABILITY_SCORE,
            value=value,
            components=components,
            summary=summary
        )

