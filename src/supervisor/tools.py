"""Custom tools for the supervisor agent."""

from typing import Dict, Any, List
from langchain.tools import tool, ToolRuntime
from langchain.messages import HumanMessage, ToolMessage
from langgraph.types import Command, interrupt
import uuid
from pydantic import BaseModel, Field

from src.utils.config import supervisor_model
from src.researcher.graph import research_agent_graph
from src.supervisor.schemas import ResearchAssignment


# -------------------------------- LAUNCH RESEARCHER TOOL --------------------------------
# Launches a researcher graph using .ainvoke() method and returns state updates via Command
# State updates are merged using reducers (merge_str_dict, merge_int_dict, keep_first_str)
@tool
async def launch_researcher(runtime: ToolRuntime, assignment: ResearchAssignment) -> Command:
    """Start a researcher on a dimension. Pass ResearchAssignment with dimension_key, workspace_path, lens_title, lens_brief, research_context."""
    # Use provided dimension key and workspace path directly
    dimension_key = assignment.dimension_key
    sandbox_path = assignment.workspace_path
    subagent_thread_id = f"research:{dimension_key}:{uuid.uuid4().hex[:8]}"
    
    # Extract session name from workspace_path (format: /session-name/dimension-key/)
    session_name = sandbox_path.strip('/').split('/')[0] if '/' in sandbox_path else "session"
    
    config = {
        "configurable": {"thread_id": subagent_thread_id},
        "context": {"sandbox_path": sandbox_path},
    }

    # Send assignment-specific details
    instruction = f"""### Your Research Assignment

**Research Context**: {assignment.research_context}

**Your Dimension**: {assignment.lens_title}
**Your Lens**: {assignment.lens_brief}
**Workspace**: {sandbox_path}
**Dimension Key**: {dimension_key}

**This is a FORUM—you'll likely be called back for refinement.**

**This round**:
- Run 1-2 web searches to explore your lens
- Append findings to `findings.md` (mark as "Round 1")
- Update `sources.json`

**Expect**:
- Moderator will review, spot patterns across dimensions, and may call you back with:
  * "Dig deeper on X"
  * "How does this connect to Agent Y's findings?"
  * "Explore this tension between..."
- You'll do 1-2 more searches and append to `findings.md` (mark as "Round 2" or "Round 3")
- After 2-3 rounds total, your `findings.md` is your complete report

All files stay in your workspace. Follow the workflow in your system prompt.
"""
    initial_message = HumanMessage(content=instruction)

    # Invoke subagent with minimal error handling to avoid superstep rollback
    try:
        await research_agent_graph.ainvoke({"messages": [initial_message]}, config)
    except Exception as e:
        return Command(update={
            "messages": [
                ToolMessage(
                    f"Failed to launch researcher '{dimension_key}': {e}",
                    tool_call_id=runtime.tool_call_id,
                )
            ]
        })

    # Return state updates via Command (LangGraph merges parallel writes using reducers)
    update = {
        "subagent_threads": {dimension_key: subagent_thread_id},  # For dynamic prompt display
        "resume_counts": {subagent_thread_id: 0},                  # Initialize refinement counter
        "messages": [
            ToolMessage(
                f"✓ Researcher '{dimension_key}' completed Round 1 → {subagent_thread_id}\n"
                f"Workspace: {sandbox_path}\n"
                f"Status: Initial findings written to findings.md",
                tool_call_id=runtime.tool_call_id,
            )
        ],
    }
    
    # Only first launch sets session_name (keep_first_str reducer handles concurrent writes)
    if not runtime.state.get("session_name"):
        update["session_name"] = session_name
    
    return Command(update=update)



# -------------------------------- RESUME RESEARCHER TOOL --------------------------------
# Resumes a researcher graph using .ainvoke() method and returns state updates via Command
# State updates are merged using reducers (merge_int_dict)
@tool
async def resume_researcher(runtime: ToolRuntime, thread_id: str, refinement_instructions: str = "") -> Command:
    """Resume an existing researcher with refinement instructions.
    
    Args:
        thread_id: The researcher's thread_id from subagent_threads (e.g., "research:dev-reality:abc123")
        refinement_instructions: Specific follow-up prompt based on cross-dimension findings
    """
    session_name = runtime.state.get("session_name", "session")
    
    # Parse dimension_key from thread_id format: "research:{dimension_key}:{uuid}"
    parts = thread_id.split(":")
    if len(parts) >= 2:
        dimension_key = parts[1]
    else:
        raise ValueError(f"Invalid thread_id format: {thread_id}")

    sandbox_path = f"/{session_name}/{dimension_key}/"
    config = {
        "configurable": {"thread_id": thread_id},
        "context": {"sandbox_path": sandbox_path},
    }

    messages = []
    if refinement_instructions:
        current_count = (runtime.state.get("resume_counts") or {}).get(thread_id, 0)
        round_number = current_count + 2  # +1 for this round, +1 because initial was round 1
        content = (
            f"### Refinement Prompt (Moderator → {dimension_key})\n\n"
            f"{refinement_instructions}\n\n"
            f"**Your workspace**: {sandbox_path}\n"
            f"**This is Round {round_number}**: Run 1-2 more searches addressing this prompt, "
            f"append findings to `findings.md` (mark as 'Round {round_number}'), and update `sources.json`. "
            f"The forum is evolving—your fresh perspective helps us spot patterns."
        )
        messages.append(HumanMessage(content=content))

    inputs = {"messages": messages} if messages else None
    try:
        await research_agent_graph.ainvoke(inputs, config)
    except Exception as e:
        return Command(update={
            "messages": [
                ToolMessage(
                    f"Failed to resume researcher '{dimension_key}' (thread {thread_id}): {e}",
                    tool_call_id=runtime.tool_call_id,
                )
            ]
        })

    return Command(update={
        "resume_counts": {thread_id: 1},  # merged additively by merge_int_dict
        "messages": [
            ToolMessage(
                f"✓ Researcher '{dimension_key}' completed Round {current_count + 2} → {thread_id}\n"
                f"Status: Refinement findings appended to findings.md",
                tool_call_id=runtime.tool_call_id,
            )
        ],
    })
