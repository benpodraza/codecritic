import ast
import json
import py_compile
import importlib.util
import contextlib
import sys
import io
import uuid
from typing import Dict

from pydantic import BaseModel

from app.enums.logging_enums import RunContext
from app.providers.score_provider_base import ScoreProviderBase
from app.db.schemas import CodeStabilityScoreConfig, ScoreOutputSchema, CodeStabilityScoreComponents
from app.enums.scoring_enums import SCORING_METRIC_TYPE
from app.utilities.metadata.footer.code_annnotation_utils import split_content_and_notes
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

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
        bool_components: Dict[str, bool] = {}

        file_path = input.get("file_path")
        if not file_path or not isinstance(file_path, str):
            raise ValueError("❌ 'file_path' is required and must be a non-empty string.")

        try:
            input_file, resolved_type = self._resolve_file_path(file_path)
            raw_code = fm.load(resolved_type, input_file)
            bool_components["utf8_valid"] = True
        except Exception:
            bool_components["utf8_valid"] = False
            return self._final_score(bool_components)

        stripped_code, _ = split_content_and_notes(raw_code)
        working_filename = f"{uuid.uuid4().hex}_stripped.py"
        fm.save(FILETYPE.WORKING, working_filename, stripped_code.rstrip() + "\n")
        stripped_code = fm.load(FILETYPE.WORKING, working_filename)

        try:
            with suppress_output():
                try:
                    compile(stripped_code, working_filename, "exec")
                    ast.parse(stripped_code)
                    bool_components["syntax_ok"] = True
                except (SyntaxError, IndentationError):
                    bool_components["syntax_ok"] = False
                    return self._final_score(bool_components)

                try:
                    py_compile.compile(
                        str(fm._resolve(FILETYPE.WORKING, working_filename)),
                        doraise=True
                    )
                    bool_components["py_compile_ok"] = True
                except Exception:
                    bool_components["py_compile_ok"] = False
                    return self._final_score(bool_components)

                try:
                    abs_path = str(fm._resolve(FILETYPE.WORKING, working_filename))
                    spec = importlib.util.spec_from_file_location("mod", abs_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)  # type: ignore
                    bool_components["can_import"] = True
                except Exception:
                    bool_components["can_import"] = False
                    return self._final_score(bool_components)

        finally:
            fm.delete(FILETYPE.WORKING, working_filename)

        return self._final_score(bool_components)

    def _resolve_file_path(self, maybe_code: str) -> tuple[str, FILETYPE]:
        if "\n" not in maybe_code:
            try:
                for ft in [FILETYPE.WORKING, FILETYPE.SNAPSHOT, FILETYPE.INPUT]:
                    candidate = fm._resolve(ft, maybe_code)
                    if candidate.exists():
                        return maybe_code, ft
            except Exception:
                pass

        name = f"{uuid.uuid4().hex}.py"
        fm.save(FILETYPE.SNAPSHOT, name, maybe_code)
        return name, FILETYPE.SNAPSHOT

    def _final_score(self, bool_components: Dict[str, bool]) -> ScoreOutputSchema:
        components = CodeStabilityScoreComponents(
            type="code_stability",
            utf8_valid=float(bool_components.get("utf8_valid", False)),
            syntax_ok=float(bool_components.get("syntax_ok", False)),
            py_compile_ok=float(bool_components.get("py_compile_ok", False)),
            can_import=float(bool_components.get("can_import", False)),
        )
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
