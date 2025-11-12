"""Reducer functions for LangGraph state merging.

When multiple tools execute in parallel (e.g., launching 3 researchers simultaneously),
each tool returns state updates. LangGraph uses these reducers to merge concurrent writes
to the same state field, preventing conflicts.
"""
from typing import Dict


def merge_int_dict(existing: Dict[str, int] | None, new: Dict[str, int] | None) -> Dict[str, int]:
    """Additive merge for integer dictionaries (sums overlapping keys).
    
    Used for: resume_counts (tracks refinement count per thread_id)
    Example: {"thread_abc": 1} + {"thread_abc": 1} → {"thread_abc": 2}
    """
    base = dict(existing or {})
    for k, v in (new or {}).items():
        base[k] = base.get(k, 0) + int(v)
    return base 


def merge_str_dict(existing: Dict[str, str] | None, new: Dict[str, str] | None) -> Dict[str, str]:
    """Merge string dictionaries (new overwrites existing keys).
    
    Used for: subagent_threads (dimension → thread_id mapping)
    Example: {"dim_a": "tid_1"} + {"dim_b": "tid_2"} → {"dim_a": "tid_1", "dim_b": "tid_2"}
    """
    merged = dict(existing or {})
    merged.update(new or {})
    return merged


def keep_first_str(a: str | None, b: str | None) -> str:
    """Keep first non-empty string when multiple tools write to the same field.
    
    Used for: session_name (only first launch_researcher sets it)
    Example: "session-foo" + "" → "session-foo"
    """
    return a or b or ""
