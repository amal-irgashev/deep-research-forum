"""Pydantic schemas for structured web search results (minimal, content-rich)."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    """A source document from web search."""
    
    title: str = Field(description="Title of the source document")
    url: str = Field(description="URL of the source")
    author: Optional[str] = Field(default=None, description="Author name if available")
    published_date: Optional[str] = Field(default=None, description="Publication date if available")
    snippet: Optional[str] = Field(default=None, description="Short excerpt from the source content")
    text_length: Optional[int] = Field(default=None, description="Total characters in the source text")


class ResearchResult(BaseModel):
    """Minimal, general-purpose output for research agents.
    
    - summary: 600–900 words, rich content with inline citations (full URL + year)
    - takeaways: 6–12 crisp bullet points
    - sources: metadata + snippets for transparency and follow-up reading
    """
    query: str = Field(description="The original search query")
    summary: str = Field(description="A detailed multi-paragraph synthesis (600–900 words) with inline citations like (https://url, YYYY)")
    takeaways: List[str] = Field(description="6–12 key bullet points", min_length=3, max_length=14)
    sources: List[Source] = Field(description="All sources consulted with metadata and snippets", min_length=1)

