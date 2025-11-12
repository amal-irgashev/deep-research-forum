# utility functions for merging dictionaries and normalizing topic keys
import re
from typing import Dict, Any

# merge function for resume counts (thread_id → count)
def merge_int_dict(existing: Dict[str, int] | None, new: Dict[str, int] | None) -> Dict[str, int]:
    """Additive merge for integer dicts (sums overlapping keys)."""
    base = dict(existing or {})
    for k, v in (new or {}).items():
        base[k] = base.get(k, 0) + int(v)
    return base 

# merge function for subagent threads (str to str)
def merge_str_dict(existing:Dict[str,str],new:Dict[str,str])->Dict[str,str]:
    """Overwrite for string dictionaries."""
    merged: Dict[str,str] = dict(existing or {})
    merged.update(new)
    return merged

# reducer for concurrent updates to a single string value (keep first non-empty)
def keep_first_str(a: str, b: str) -> str:
    """
    Prefer the first non-empty string when multiple writes occur in the same step.
    This resolves concurrent updates to a single LastValue channel key (e.g., 'session_name').
    """
    return a or b


#--------------------------------
# regex pattern for slugifying topic keys
_TOPIC_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")

def normalize_topic_key(topic: str) -> str:
    """convert a topic string into a slugified key."""
    slug = _TOPIC_SLUG_PATTERN.sub("-", topic.lower()).strip("-")
    return slug or "topic" # default to "topic" if no slug is generated