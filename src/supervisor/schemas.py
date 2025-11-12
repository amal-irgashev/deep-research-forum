from pydantic import BaseModel, Field

# schema for the research assignment to a subagent
class ResearchAssignment(BaseModel):
    """Minimal contract for delegating a research dimension to a subagent."""

    dimension_key: str = Field(description="Slug for this dimension, e.g., 'eu-governance'")
    workspace_path: str = Field(description="Absolute workspace path, e.g., '/session-abc123/eu-governance/'")
    lens_title: str = Field(description="Human-readable dimension title, e.g., 'AI Regulation'")
    lens_brief: str = Field(description="1–2 sentence lens framing for this dimension")


