from __future__ import annotations

import json
from typing import Any, Dict, List

from ...abstract_classes.agent_base import AgentBase
from ...enums.agent_enums import AgentRole
from ...abstract_classes.context_provider_base import ContextProviderBase
from ...factories.logging_provider import (
    ConversationLog,
    CodeQualityLog,
    ScoringLog,
    ErrorLog,
    RecommendationLog,
    LoggingProvider,
)
from ...utilities.snapshots.snapshot_writer import SnapshotWriter


class RecommendationAgent(AgentBase):
    """Analyze historical logs and generate code improvement recommendations."""

    def __init__(
        self,
        target: str,
        logger: LoggingProvider | None = None,
        snapshot_writer: SnapshotWriter | None = None,
        context_provider: ContextProviderBase | None = None,
    ) -> None:
        super().__init__(logger)
        self.target = target
        self.snapshot_writer = snapshot_writer or SnapshotWriter()
        self.context_provider = context_provider
        self.recommendation_logs: List[RecommendationLog] = []
        self.error_logs: List[ErrorLog] = []
        self.conversation_logs: List[ConversationLog] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _analyze_symbol_graph(
        self, graph: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on a symbol graph."""
        recs: List[Dict[str, Any]] = []

        # Build call relationships by symbol name
        callers: Dict[str, set[str]] = {}
        definitions: Dict[str, Dict[str, Any]] = {}
        for qual, info in graph.items():
            definitions[qual] = info
            for called in info.get("calls", []):
                callers.setdefault(called, set()).add(qual)

        # Unused imports and symbols
        for qual, info in definitions.items():
            name = info.get("name")
            typ = info.get("type")
            if typ == "import" and name not in callers:
                recs.append(
                    {
                        "action": "remove_unused_import",
                        "target": qual,
                        "rationale": f"Import '{name}' is never referenced",
                    }
                )
            if typ in {"function", "async_function", "class"} and name not in callers:
                recs.append(
                    {
                        "action": "remove_unused_symbol",
                        "target": qual,
                        "rationale": f"Symbol '{name}' is defined but not used",
                    }
                )

        # Circular dependencies detection
        graph_by_name = {
            info.get("name"): qual
            for qual, info in definitions.items()
            if info.get("type") in {"function", "async_function", "class"}
        }
        edges: Dict[str, set[str]] = {}
        for qual, info in definitions.items():
            if info.get("type") not in {"function", "async_function", "class"}:
                continue
            for called in info.get("calls", []):
                dest = graph_by_name.get(called)
                if dest:
                    edges.setdefault(qual, set()).add(dest)

        def _find_cycles() -> List[List[str]]:
            cycles: List[List[str]] = []
            path: List[str] = []

            def visit(node: str, stack: set[str]) -> None:
                stack.add(node)
                path.append(node)
                for nxt in edges.get(node, set()):
                    if nxt in stack:
                        idx = path.index(nxt)
                        cycles.append(path[idx:] + [nxt])
                    else:
                        visit(nxt, stack)
                stack.remove(node)
                path.pop()

            for n in list(edges):
                visit(n, set())
            return cycles

        for cycle in _find_cycles():
            if len(cycle) > 1:
                recs.append(
                    {
                        "action": "refactor_circular_dependency",
                        "symbols": cycle,
                        "rationale": " -> ".join(cycle),
                    }
                )

        return recs

    def _run_agent_logic(self, *args, **kwargs) -> None:
        conv_logs: List[ConversationLog] = kwargs.get("conversation_log", [])
        qual_logs: List[CodeQualityLog] = kwargs.get("code_quality_log", [])
        scoring_logs: List[ScoringLog] = kwargs.get("scoring_log", [])

        recommendations: List[str] = []
        context_parts: List[str] = []
        structured_recs: List[Dict[str, Any]] = []

        ctx = kwargs.get("context")
        if ctx is None and self.context_provider is not None:
            ctx = self.context_provider.get_context()
        graph = {}
        if isinstance(ctx, dict):
            graph = ctx.get("symbol_graph", {})
        if graph:
            structured_recs.extend(self._analyze_symbol_graph(graph))
            if structured_recs:
                context_parts.append("symbol graph analysis")

        for qlog in qual_logs:
            if qlog.lint_errors > 0:
                recommendations.append("Fix lint errors")
                context_parts.append("lint issues detected")
            if qlog.maintainability_index < 70:
                recommendations.append("Refactor to improve maintainability")
                context_parts.append("low maintainability")
            if qlog.cyclomatic_complexity > 10:
                recommendations.append("Simplify to reduce complexity")
                context_parts.append("high complexity")

        for slog in scoring_logs:
            if slog.value < 0.5:
                recommendations.append(f"Improve score for {slog.metric.value}")
                context_parts.append(f"low score {slog.metric.value}")

        for clog in conv_logs:
            if clog.intervention and clog.content:
                recommendations.append(clog.content)
                context_parts.append("prior intervention")

        unique: List[str] = []
        for r in recommendations:
            if r not in unique:
                unique.append(r)

        for text in unique:
            structured_recs.append({"action": "general", "message": text})

        if not structured_recs:
            return

        rec_text = json.dumps(structured_recs, indent=2)
        ctx_text = "; ".join(context_parts)

        rec_log = RecommendationLog(
            experiment_id="exp",
            round=0,
            symbol=self.target,
            file_path=self.target,
            line_start=0,
            line_end=0,
            recommendation=rec_text,
            context=ctx_text,
        )
        self.recommendation_logs.append(rec_log)

        conv_log = ConversationLog(
            experiment_id="exp",
            round=0,
            agent_role=AgentRole.RECOMMENDER,
            target=self.target,
            content=rec_text,
            originating_agent="recommender",
            intervention=bool(structured_recs),
            intervention_type="recommendation" if structured_recs else None,
            intervention_reason="analysis" if structured_recs else None,
        )
        self.conversation_logs.append(conv_log)

        try:
            self.log_recommendation(rec_log)
            self.log_conversation(conv_log)
        except Exception as exc:  # pragma: no cover - db failure
            err = ErrorLog(
                experiment_id="exp",
                round=0,
                error_type=type(exc).__name__,
                message=str(exc),
                file_path=self.target,
            )
            self.error_logs.append(err)
            self.log_error(err)

        before = ctx_text
        after = rec_text
        self.snapshot_writer.write_snapshot(
            experiment_id="exp",
            round=0,
            file_path=self.target,
            before=before,
            after=after,
            symbol=self.target,
            agent_role=AgentRole.RECOMMENDER,
        )
