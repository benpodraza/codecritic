"""
ContextFilter: Global plugin for scoping what parts of the context are visible to an agent.

Used by Generator, Discriminator, Mediator, or any agent that requires filtered view
of child components, metadata, or imports.

Author: ConceptBuilder Core
"""

from typing import Dict, Any, Optional


class ContextFilter:
    def __init__(self, strategy: Optional[str] = None):
        """
        Initialize the filter with a strategy.
        Supported:
            - default
            - only_children_with_logger
            - only_breadcrumb_children
            - minimal
        """
        self.strategy = strategy or "default"

    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if self.strategy == "default":
            return context
        elif self.strategy == "only_children_with_logger":
            return self._filter_logger_children(context)
        elif self.strategy == "only_breadcrumb_children":
            return self._filter_breadcrumb_children(context)
        elif self.strategy == "minimal":
            return self._minimal_context(context)
        raise ValueError(f"Unknown context filter strategy: {self.strategy}")

    def _filter_logger_children(self, context: Dict[str, Any]) -> Dict[str, Any]:
        filtered = [c for c in context.get("children", []) if "logger." in c.get("content", "")]
        return {
            **context,
            "children": filtered,
            "logger_calls": sum(c["content"].count("logger.") for c in filtered),
            "breadcrumbs": sum(c["content"].count("BREADCRUMB:") for c in filtered)
        }

    def _filter_breadcrumb_children(self, context: Dict[str, Any]) -> Dict[str, Any]:
        filtered = [c for c in context.get("children", []) if "BREADCRUMB:" in c.get("content", "")]
        return {
            **context,
            "children": filtered,
            "logger_calls": sum(c["content"].count("logger.") for c in filtered),
            "breadcrumbs": sum(c["content"].count("BREADCRUMB:") for c in filtered)
        }

    def _minimal_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "symbol": context.get("symbol"),
            "source_file": context.get("source_file"),
            "metadata": context.get("metadata", [])
        }
