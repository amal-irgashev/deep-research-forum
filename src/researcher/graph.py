"""Research agent using create_agent with filesystem middleware."""

from datetime import datetime, timezone
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest

from src.researcher.prompt import RESEARCH_AGENT_PROMPT
from src.tools.web_search.web_search import web_search
from src.utils.config import research_model, filesystem_mw


# -------------------------------- RESEARCH AGENT PROMPT MIDDLEWARE --------------------------------
# Dynamic prompt middleware: injects current datetime before each LLM call
@dynamic_prompt
def researcher_datetime_prompt(request: ModelRequest) -> str:
    """Append current datetime to system prompt."""
    return RESEARCH_AGENT_PROMPT.format(
        current_datetime=datetime.now(timezone.utc).isoformat()
    )

# -------------------------------- RESEARCH AGENT GRAPH --------------------------------
research_agent_graph = create_agent(
    model=research_model,
    tools=[web_search],
    system_prompt="",  # Empty base; researcher_datetime_prompt builds full prompt dynamically
    middleware=[researcher_datetime_prompt, filesystem_mw],
)

__all__ = ["research_agent_graph"]
