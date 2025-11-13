# Deep Research Forum

A deep research system that works like a moderated forum. The Supervisor assigns different **perspectives** to isolated researcher subagents. Each researcher explores independently in the isolated environment, finding evidence through their assigned viewpoint.

The Supervisor reads all findings, spots tensions ("Agent A found success stories, but Agent B found abandonment patterns"), then asks subagents targeted follow-up questions. The final report synthesizes all perspectives into an unbiased view forced to account for contradictory evidence rather than cherry-picking. Bias reduction happens through **isolation** and **mandatory multi-perspective synthesis** (can't ignore conflicting findings).

---

## Quick Start

**1. Install `uv` (skip if already installed)**

macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. Clone the repo**
```bash
git clone https://github.com/amal-irgashev/deep-research-forum.git
cd deep-research-forum
```

**3. Install dependencies**
```bash
uv sync
```

**4. Configure environment**
```bash
cp .env.example .env
```

Get API keys:
- **Anthropic** (Claude): https://console.anthropic.com/
- **OpenAI** (GPT): https://platform.openai.com/api-keys
- **Exa** (Search): https://dashboard.exa.ai/api-keys

**5. Run the agent**
```bash
uv run langgraph dev
```

Open LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

**Note**: It's recommended to clean up the `research_forum/` folder between research sessions to avoid workspace conflicts:
```bash
rm -rf research_forum/session-*
```

---

## Architecture

### Core Pattern

Supervisor (Claude Sonnet 4.5) orchestrates isolated researchers (GPT-5 mini), each exploring a distinct **perspective lens**. Researchers write `findings.md` + `sources.json` to sandboxed folders under `research_forum/session-<slug>/<dimension>/`.

**Typical run**: 10-15 minutes, ~$0.60 (3-5 dimensions × 1-2 rounds).

### Tools

**Web search** (Exa + LLM summarization):
```python
web_search(
    query="AI regulation enforcement mechanisms EU vs US",
    max_results=3  # Fetches up to 8000 chars per result
)
# Returns: ResearchResult with structured outputs: summary, takeaways, and sources
```

**Supervisor delegation**:
```python
launch_researcher(assignment)   # Start new dimension
resume_researcher(thread_id, refinement_instructions)  # Continue with new prompt
```

**File operations** (both agents via `FilesystemMiddleware`):
```python
write_file(path, content)
read_file(path)
edit_file(path, old_string, new_string)
ls(path), glob(pattern), grep(pattern)
```

### Delegation Model

**Launch subagent**:
```python
launch_researcher(
    assignment=ResearchAssignment(
        dimension_key="developer-reality",
        workspace_path="/session-frameworks-2025/developer-reality/",
        lens_title="Developer Experience Reality",
        lens_brief="Find GitHub issues, blog posts, 'I tried X and it failed' stories..."
    )
)
# Returns: thread_id = "research:developer-reality:abc123"
```

**Resume for refinement**:
```python
resume_researcher(
    thread_id="research:developer-reality:abc123",
    refinement_instructions="You found vendor success stories. Now find independent post-mortems and failure cases. One researcher discovered high adoption claims—dig into actual implementation struggles."
)
# Hard limit: 0-2 refinements per dimension (tracked in SupervisorAgentState and injected into the system prompt)
```

### State & Context

**State tracking**:
```python
class SupervisorAgentState(AgentState):
    subagent_threads: Dict[str, str]  # dimension → thread_id
    resume_counts: Dict[str, int]     # thread_id → refinement_count
    session_name: str                  # e.g., "session-agent-frameworks-2025"
```
Reducers (`merge_str_dict`, `merge_int_dict`, `keep_first_str`) enable safe concurrent tool calls.

**Dynamic prompting**: `@dynamic_prompt` middleware injects live progress into system prompt before each model call:
```
### Current Subagent Progress
- production-failures → research:production-failures:abc123 (refinements: 1/2)
- developer-reality → research:developer-reality:def456 (refinements: 0/2)
```

**Filesystem as message bus**: `FilesystemMiddleware` (deepagents) with `FilesystemBackend`:
```python
FilesystemBackend(root_dir="research_forum/", virtual_mode=True)
```
Sandboxes all paths under root. Researchers write to `context["sandbox_path"]`; Supervisor reads all dimensions.

### Research Lifecycle

1. **Recon**: Assess landscape (1-2 `web_search` calls)
2. **Align**: Propose lenses to user, wait for confirmation
3. **Launch**: Start all dimensions (parallel tool calls)
4. **Assess**: Read outputs, check source diversity/disconfirming evidence, note gaps in `forum_index.json`
5. **Refine**: Resume 0-2 dimensions with targeted prompts
6. **Synthesize**: Present final report to user (not written to file)

### Research Forum Sandbox Structure

```
research_forum/
  session-<slug>/
    forum_index.json       # Supervisor's evidence quality notes
    <dimension>/
      findings.md          # Round-tagged findings (cumulative)
      sources.json         # Citations with URLs
```

### Implementation

- **Supervisor**: `src/supervisor/graph.py`, `src/supervisor/prompt.py`
- **Researcher**: `src/researcher/graph.py`, `src/researcher/prompt.py`
- **Tools**: `src/supervisor/tools.py`, `src/tools/web_search/`
- **Config**: `src/utils/config.py` (models, middleware, sandbox)
- **Entry**: `langgraph.json` → `src.supervisor.graph:graph`

Run: `uv run langgraph dev` and watch `research_forum/session-*/` populate in real-time.

