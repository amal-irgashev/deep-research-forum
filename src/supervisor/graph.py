"""Supervisor agent graph."""

from datetime import datetime, timezone
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from typing import Dict, Any
from typing_extensions import Annotated, NotRequired
from langchain.agents import AgentState

from src.utils.utils import merge_str_dict, merge_int_dict, keep_first_str
from src.supervisor.prompt import SUPERVISOR_SYSTEM_PROMPT
from src.tools.web_search.web_search import web_search
from src.supervisor.tools import launch_researcher, resume_researcher  # propose_research_plan commented out
from src.utils.config import supervisor_model, filesystem_mw

# Supervisor state schema (extends AgentState with tracking fields)
class SupervisorAgentState(AgentState):
    """Extended agent state that keeps track of subagent thread IDs and resume counts."""

    subagent_threads: NotRequired[Annotated[Dict[str, str], merge_str_dict]]  # agent_key → thread_id
    resume_counts: NotRequired[Annotated[Dict[str, int], merge_int_dict]]  # thread_id → resume_count
    session_name: NotRequired[Annotated[str, keep_first_str]]



_BASE_SUPERVISOR_PROMPT = SUPERVISOR_SYSTEM_PROMPT.format(
    current_datetime=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
)

# Dynamic prompt middleware: injects live researcher status before each LLM call
@dynamic_prompt
def supervisor_progress_prompt(request: ModelRequest) -> str:
    """Append active researcher progress to system prompt.
    
    Shows supervisor which dimensions are running and refinement counts.
    Enables LLM to make informed decisions about resume_researcher calls.
    """
    base = _BASE_SUPERVISOR_PROMPT
    threads = request.state.get("subagent_threads") or {}
    counts = request.state.get("resume_counts") or {}
    
    if not threads:
        return base
    
    # Build progress summary
    lines = []
    for dimension, thread_id in sorted(threads.items()):
        count = counts.get(thread_id, 0)
        status = f"refinements: {count}/2"
        if count == 2:
            status += " (limit reached)"
        elif count > 2:
            status += " (limit exceeded)"
        lines.append(f"- {dimension} → {thread_id} ({status})")
    
    return f"{base}\n\n### Current Subagent Progress\n" + "\n".join(lines)

agent = create_agent(
    model=supervisor_model,
    system_prompt=_BASE_SUPERVISOR_PROMPT,
    tools=[
        web_search,
        launch_researcher,
        resume_researcher,
    ],
    state_schema=SupervisorAgentState,
    middleware=[
        supervisor_progress_prompt,  # inject subagent statuses into system prompt
        filesystem_mw,  # file operations
    ],
)

graph = agent