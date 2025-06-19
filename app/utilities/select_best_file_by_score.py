from pathlib import Path
import inspect

from app.providers.score_provider_base import ScoreProviderBase
from app.utilities.file_management.file_utils import get_file_manager

fm = get_file_manager()

def select_best_file_by_score(
    file_a: str,
    file_b: str,
    score_provider: ScoreProviderBase,
    context
) -> str:
    """
    Compare two file paths using a scoring provider and return the file path (as string) with the higher score.
    """

    try:
        ftype_a = fm.resolve_existing_filetype(file_a)
        ftype_b = fm.resolve_existing_filetype(file_b)
    except FileNotFoundError as e:
        print(f"❌ Could not resolve file type: {e}")
        raise FileNotFoundError("One or both input files do not exist.")

    exists_a = fm.exists(ftype_a, file_a)
    exists_b = fm.exists(ftype_b, file_b)


    if not exists_a or not exists_b:
        raise FileNotFoundError("One or both input files do not exist.")

    # Score using logical file names
    score_a = score_provider.run({"file_path": file_a}, context=context).value
    score_b = score_provider.run({"file_path": file_b}, context=context).value

    return file_a if score_a >= score_b else file_b
