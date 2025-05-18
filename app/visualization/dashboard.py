from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


_LOG_TABLES = {
    "state": "state_log",
    "transition": "state_transition_log",
    "prompt": "prompt_log",
    "scoring": "scoring_log",
    "recommendation": "recommendation_log",
}


def load_logs(db_path: str | Path) -> Dict[str, pd.DataFrame]:
    """Load structured logs from the experiment database."""
    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(path)
    conn = sqlite3.connect(path)
    logs: Dict[str, pd.DataFrame] = {}
    for key, table in _LOG_TABLES.items():
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        except Exception:
            df = pd.DataFrame()
        logs[key] = df
    conn.close()
    return logs


def build_state_transition_sankey(df: pd.DataFrame) -> go.Figure:
    """Return a Sankey diagram for state transitions."""
    if df.empty:
        return go.Figure()
    states = pd.unique(pd.concat([df["from_state"], df["to_state"]]))
    indices = {state: i for i, state in enumerate(states)}
    source = [indices[s] for s in df["from_state"]]
    target = [indices[t] for t in df["to_state"]]
    value = [1] * len(df)
    return go.Figure(
        go.Sankey(
            node={"label": list(states)},
            link={"source": source, "target": target, "value": value},
        )
    )


def build_scoring_line_plot(df: pd.DataFrame) -> go.Figure:
    """Return a line chart for scoring metrics over rounds."""
    if df.empty:
        return go.Figure()
    return px.line(df, x="round", y="value", color="metric")


def build_recommendation_bar_plot(df: pd.DataFrame) -> go.Figure:
    """Return a bar plot summarizing recommendation counts per symbol."""
    if df.empty:
        return go.Figure()
    counts = df.groupby("symbol").size().reset_index(name="count")
    return px.bar(counts, x="symbol", y="count")
