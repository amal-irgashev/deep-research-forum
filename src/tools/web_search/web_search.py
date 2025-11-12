"""Web search tool with structured JSON output for research agents."""

import os
from functools import lru_cache
from exa_py import Exa
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage

from src.tools.web_search.prompt import WEB_SEARCH_SUMMARIZER_PROMPT
from src.tools.web_search.schema import ResearchResult, Source
from src.utils.config import web_search_summarization_model


@lru_cache(maxsize=1)
def _get_client():
    """Get the Exa client (cached)."""
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        raise RuntimeError("EXA_API_KEY not set")
    return Exa(api_key=api_key)


@tool
def web_search(query: str, max_results: int = 3) -> str:
    """Search the web and return structured findings with sources (JSON).

    Args:
        query: Natural language search query to execute
        max_results: Maximum number of search results to retrieve (default: 3)

    Returns:
        JSON string containing structured research findings, sources, and notes

    Simple pipeline:
    1) Use Exa to search and fetch full text contents for top results
    2) Provide all content to an LLM with an instruction prompt
    3) Enforce a Pydantic schema via structured_output for:
       - findings: claim, evidence, source_urls, confidence
       - sources: title, url, optional author/published_date
       - notes: short caveats/tensions
    """
    client = _get_client()
    
    # 1) Retrieve search results with full text
    response = client.search_and_contents(
        query=query,
        num_results=max_results,
        text={"max_characters": 8000}, 
        type="auto",
    )
    if not response.results:
        return (
            f'{{"query": "{query}", "findings": [{{'
            f'"claim": "No results found", '
            f'"evidence": "Search returned no results", '
            f'"source_urls": [], '
            f'"confidence": "high"}}], "sources": []}}'
        )
    
    # 2) Collect content and track sources
    all_content = []
    sources = []
    
    for result in response.results:
        title = result.title or "Untitled"
        url = result.url or ""
        text = result.text or ""
        text_len = len(text or "")
        
        if text:
            # Format each document for the model: [Title] (URL)\n<full text>
            all_content.append(f"[{title}] ({url})\n{text}")
            
            # Track structured source metadata (best effort)
            sources.append(
                Source(
                    title=title,
                    url=url,
                    author=getattr(result, "author", None),
                    published_date=str(getattr(result, "published_date", None)) 
                    if getattr(result, "published_date", None) else None,
                    snippet=(text[:1000] if text_len > 0 else None),
                    text_length=text_len,
                )
            )
    
    if not all_content:
        return (
            f'{{"query": "{query}", "findings": [{{'
            f'"claim": "No content found", '
            f'"evidence": "Sources returned empty content", '
            f'"source_urls": [], '
            f'"confidence": "high"}}], "sources": []}}'
        )
    
    # 3) Combine content and extract structured findings via schema
    combined = "\n\n---\n\n".join(all_content)
    messages = [
        SystemMessage(content=WEB_SEARCH_SUMMARIZER_PROMPT),
        HumanMessage(content=f"Query: {query}\n\nContent:\n{combined}"),
    ]
    
    # Enforce schema with structured_output to ensure clean JSON
    structured_model = web_search_summarization_model.with_structured_output(ResearchResult)
    result = structured_model.invoke(messages)
    
    # Always attach concrete sources with snippets for transparency
    result.sources = sources
    
    return result.model_dump_json(indent=2)