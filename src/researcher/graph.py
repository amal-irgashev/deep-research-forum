"""Research agent using create_agent with filesystem middleware."""

from datetime import datetime, timezone
from langchain.agents import create_agent

from src.researcher.prompt import RESEARCH_AGENT_PROMPT
from src.tools.web_search.web_search import web_search
from src.utils.config import research_model, filesystem_mw


# Format system prompt with current datetime
_BASE_RESEARCH_PROMPT = RESEARCH_AGENT_PROMPT.format(
    current_datetime=datetime.now(timezone.utc).isoformat()
)

# Create research agent using create_agent
research_agent_graph = create_agent(
    model=research_model,
    tools=[web_search],
    system_prompt=_BASE_RESEARCH_PROMPT,
    middleware=[filesystem_mw],
)

__all__ = ["research_agent_graph"]
