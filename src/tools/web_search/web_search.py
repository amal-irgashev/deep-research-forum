"""Web search tool using two-stage pipeline: Exa retrieval → LLM summarization.

Pipeline:
1. Exa API fetches top search results with full text content (up to 5000 chars/result)
2. LLM with structured output extracts findings + sources into ResearchResult schema

This separation allows:
- Cost control via max_characters (fewer tokens to LLM)
- Quality control via LLM-powered extraction (vs raw search snippets)
- Structured output enforcement (Pydantic schema validation)
"""
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
    """Get cached Exa client (avoid reinitializing on every search)."""
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        raise RuntimeError("EXA_API_KEY not set")
    return Exa(api_key=api_key)


@tool
def web_search(query: str, max_results: int = 2) -> str:
    """Search the web and return structured findings with sources (JSON).

    Args:
        query: Natural language search query to execute
        max_results: Maximum number of search results to retrieve (default: 2)

    Returns:
        JSON string containing structured research findings, sources, and notes

    Returns:
        JSON string with structured research findings and sources
    """
    client = _get_client()
    
    # Stage 1: Exa retrieval (max_characters=2500 balances cost vs content quality)
    response = client.search_and_contents(
        query=query,
        num_results=max_results,
        text={"max_characters": 2500},
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
    
    # Stage 2: Format content for LLM summarization
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
                    snippet=(text[:500] if text_len > 0 else None),  # Reduced from 1000 to 500 chars
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
    
    # Stage 3: LLM extraction with structured output (Pydantic schema enforcement)
    combined = "\n\n---\n\n".join(all_content)
    messages = [
        SystemMessage(content=WEB_SEARCH_SUMMARIZER_PROMPT),
        HumanMessage(content=f"Query: {query}\n\nContent:\n{combined}"),
    ]
    
    # with_structured_output forces LLM to return valid ResearchResult (or raise validation error)
    structured_model = web_search_summarization_model.with_structured_output(ResearchResult)
    result = structured_model.invoke(messages)
    
    # Always attach concrete sources with snippets for transparency
    result.sources = sources
    
    return result.model_dump_json(indent=2)