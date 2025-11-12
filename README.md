# Deep Research Forum

Multi-agent research system implementing a **writer-editor architecture** where a Supervisor moderates a forum of independent researcher subagents. Unlike traditional deep research systems that divide topics into subtopics, this system divides investigation into **perspectives/dimensions**—each subagent explores through a distinct lens, naturally encountering diverse evidence.

The Supervisor acts as editor and moderator: reviewing findings across dimensions, spotting patterns and contradictions, then resuming specific subagents with cross-pollinated context ("Agent A found X, but Agent B found Y—investigate this tension"). The forum structure reduces confirmation bias through architectural isolation while enabling dialogue through moderated iteration.

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
git clone https://github.com/amal-irgashev/deep-researcher-agent.git
cd deep-researcher-agent
```

**3. Install dependencies**
```bash
uv sync
```

**4. Configure environment**
```bash
cp .env.example .env
```

**5. Run the agent**
```bash
uv run langgraph dev
```

Open LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

---

## Architecture

### Design Goals

**Reduce confirmation bias through architectural isolation**: Each subagent investigates its dimension independently, unaware of other findings. The Supervisor is the only agent with cross-dimension visibility, spotting tensions and orchestrating refinement.

**Evidence quality enforcement**: The system requires source diversity (vendor vs independent vs practitioner), actively seeks disconfirming evidence, and produces outputs with explicit limitations and confidence levels.

**Output**: Decision frameworks grounded in evidence, not single answers. Reads like investigative journalism—rigorous but engaging.

**Performance**: Typical research session completes in 10-15 minutes at ~$0.60 cost (3-5 dimensions, 1-2 refinement rounds).

### System Design

A LangChain `create_agent` graph implementing this forum pattern. The Supervisor (Claude Sonnet 4.5) delegates across 3-5 dimensions to isolated Researchers (GPT-5 mini). Each researcher operates independently—no inter-agent communication—writing findings to isolated sandboxes. Only the Supervisor has cross-dimension visibility.

**Tool-invoked delegation**: The Supervisor doesn't use subgraphs or message passing. Calling `launch_researcher(assignment)` synchronously invokes the compiled `research_agent_graph` with its own `thread_id` and sandbox path. The tool blocks until that researcher completes its round and writes artifacts (`findings.md`, `sources.json`) to disk. This synchronous pattern eliminates async coordination overhead while preserving parallelism (the supervisor can launch multiple researchers via parallel tool calls in a single step).

**Research lifecycle**: Each dimension runs 1-3 rounds. Round 1: launch all dimensions. The Supervisor reads outputs, assesses evidence quality (source types, gaps, disconfirming evidence presence), updates private notes (`forum_index.json`). Round 2-3: selectively resume dimensions via `resume_researcher(thread_id, refinement_prompt)` with targeted instructions ("you found vendor success stories; now find independent post-mortems and failure cases"). Refinement budgets (0-2 per dimension) are state-tracked and hard-enforced.

### Coordination Mechanisms

**State management**: `SupervisorAgentState` extends `AgentState` with `subagent_threads` (dimension → thread_id), `resume_counts` (thread_id → count), and `session_name`. Reducers (`merge_str_dict`, `merge_int_dict`, `keep_first_str`) make concurrent tool calls safe and idempotent.

**Dynamic context**: A `@dynamic_prompt` middleware injects live subagent progress (active threads, refinement budgets) into the system prompt before every model call. Middleware reads state → augments prompt → model adapts.

**Inter-agent communication**: `FilesystemMiddleware` mounts a virtual tree under `research_forum/`. Researchers write to isolated sandboxes (`context["sandbox_path"]`); the Supervisor reads across all dimensions. The filesystem is the message bus.

### Execution Flow

1. **Reconnaissance**: 1–2 `web_search` calls to assess landscape
2. **Alignment**: Propose dimensions to user, confirm scope
3. **Launch**: 3–5 `launch_researcher` calls (synchronous, isolated)
4. **Review**: Read `findings.md`, assess evidence quality, annotate `forum_index.json`
5. **Refine**: 0–2 `resume_researcher` calls per dimension to close gaps
6. **Synthesize**: Write final report with methodology and confidence levels

### Workspace Structure

```
research_forum/
  session-<slug>/
    forum_index.json       # Supervisor notes
    <dimension>/
      findings.md          # Round-tagged research
      sources.json         # Citations
    FINAL_REPORT.md        # Final synthesis
```

### Implementation

- **Supervisor**: `src/supervisor/graph.py`, `src/supervisor/prompt.py`
- **Researcher**: `src/researcher/graph.py`, `src/researcher/prompt.py`
- **Tools**: `src/supervisor/tools.py`, `src/tools/web_search/`
- **Config**: `src/utils/config.py` (models, middleware, sandbox)
- **Entry**: `langgraph.json` → `src.supervisor.graph:graph`

Run: `uv run langgraph dev` and watch `research_forum/session-*/` populate in real-time.

