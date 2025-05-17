# app/utils/evaluation/system_evaluator.py

from abc import ABC, abstractmethod

class SystemEvaluator(ABC):
    @abstractmethod
    def score(self, original_code: str, modified_code: str) -> dict:
        """
        Run full evaluation pass and return scores.

        Args:
            original_code (str): Raw code prior to modification.
            modified_code (str): Annotated/generated result.

        Returns:
            dict: Score dictionary with numeric keys.
        """
        pass

    @abstractmethod
    def meets_stopping_condition(self, score: dict) -> bool:
        """
        Determine if score satisfies the configured stopping condition.
        """
        pass