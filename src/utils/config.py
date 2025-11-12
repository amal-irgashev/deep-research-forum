from pathlib import Path
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from deepagents.middleware import FilesystemMiddleware
from deepagents.backends import FilesystemBackend

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Shared filesystem middleware for both supervisor and research agents
REPO_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = REPO_ROOT / "research_forum"
SANDBOX_ROOT.mkdir(exist_ok=True)

filesystem_mw = FilesystemMiddleware(
    backend=FilesystemBackend(
        root_dir=str(SANDBOX_ROOT),
        virtual_mode=True,
    )
)

# Supervisor model
supervisor_model = init_chat_model(
    "anthropic:claude-sonnet-4-5-20250929",
    temperature=0.1,
    max_tokens=15000,
    disable_streaming=False,
)

# Research agent model (streaming disabled to prevent UI noise from subagents)
research_model = init_chat_model(
    "openai:gpt-5-mini",
    reasoning_effort="medium",
    temperature=0.1,
    disable_streaming=True,
)

# Web search summarization model (streaming disabled - not user-facing)
web_search_summarization_model = init_chat_model(
    "openai:gpt-5-mini",
    reasoning_effort="low",
    temperature=0.1,
    disable_streaming=True,
)