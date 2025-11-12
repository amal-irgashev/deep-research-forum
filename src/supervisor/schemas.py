from pydantic import BaseModel, Field


class ResearchAssignment(BaseModel):
    """Schema for launching a researcher subagent on a specific dimension.
    
    Example:
        ResearchAssignment(
            dimension_key="vendor-claims",
            workspace_path="/session-frameworks-2025/vendor-claims/",
            lens_title="Vendor Marketing Claims",
            lens_brief="Analyze official docs and case studies. What do vendors claim works?"
        )
    """
    dimension_key: str = Field(description="Slug for this dimension, e.g., 'vendor-claims'")
    workspace_path: str = Field(description="Sandbox path, e.g., '/session-foo/vendor-claims/'")
    lens_title: str = Field(description="Human-readable title, e.g., 'Vendor Marketing Claims'")
    lens_brief: str = Field(description="1-2 sentence lens framing for this perspective")


