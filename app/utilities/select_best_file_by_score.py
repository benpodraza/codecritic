from pathlib import Path
from typing import Callable

from app.providers.score_provider_base import ScoreProviderBase


def select_best_file_by_score(
    file_a: str,
    file_b: str,
    score_provider: ScoreProviderBase,
    context
) -> str:
    """
    Compare two file paths using a scoring provider (with .run(input, session_id).value)
    and return the file path with the higher score.

    Args:
        file_a (str): First file path to compare.
        file_b (str): Second file path to compare.
        scoring_provider: Object with a .run(dict, session_id) method that returns .value.
        system (str): System identifier passed into the scoring input.
        session_id (str): Session identifier passed into the scoring call.

    Returns:
        str: File path with the higher score.
    """
    path_a = Path(file_a).resolve()
    path_b = Path(file_b).resolve()

    score_a = score_provider.run({"file_path": str(path_a)}, context=context).value
    score_b = score_provider.run({"file_path": str(path_b)}, context=context).value

    return str(path_a if score_a >= score_b else path_b)