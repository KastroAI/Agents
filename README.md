# TurboAutomations

Reusable tools for building AI agents — comms I/O, vector search, memory, and workflow templates.

## Prerequisites

- Python 3.10+
- An OpenAI API key (for embeddings and chat completions)
- Optional: Pinecone account, Telegram bot token, Gmail OAuth credentials

## Quickstart

```bash
# Clone and install in editable mode
git clone https://github.com/OttomanAI/Agents.git
cd Agents
pip install -e ".[dev]"

# Copy the env template and fill in your keys
cp .env.example .env

# Run the tests
pytest
```

## Project structure

```
src/
  agent_tools/          # Agent utilities
    pinecone.py         # Pinecone index helper + semantic search
    simple_memory.py    # JSON-file conversation memory
  comms/                # Communication I/O
    telegram.py         # Telegram bot API (polling, sending, typing)
    gmail.py            # Gmail inbox watcher (OAuth2, polling)
workflows/              # Example agent workflows
tests/                  # Unit tests
```

## Configuration

Copy `.env.example` to `.env` and set your keys:

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `PINECONE_API_KEY` | For vector search | Pinecone API key |
| `PINECONE_INDEX_NAME` | For vector search | Pinecone index name |
| `PINECONE_NAMESPACE` | For vector search | Pinecone namespace |
| `TELEGRAM_BOT_TOKEN` | For Telegram | Telegram bot token |

## Packages

### `agent_tools`

| Module | Purpose |
|---|---|
| `pinecone.py` | `get_index()` connects to or creates a Pinecone index. `query_chunks()` embeds a prompt and returns top matching text chunks. |
| `simple_memory.py` | `Memory` class that persists conversation history to a JSON file with configurable `max_entries`. |

### `comms`

| Module | Purpose |
|---|---|
| `telegram.py` | Telegram bot polling, message sending, and typing indicators. |
| `gmail.py` | Gmail inbox watcher using OAuth2. Polls for new emails and extracts headers, body, and metadata. |

## Usage

```python
from comms import telegram
from comms.gmail import GmailWatchClient
from agent_tools.pinecone import get_index, query_chunks
from agent_tools.simple_memory import Memory
```

## Optional dependencies

```bash
pip install -e ".[pinecone]"   # Pinecone vector search
pip install -e ".[gmail]"      # Gmail integration
pip install -e ".[dev]"        # Testing and linting
```

## Contributing

1. Fork the repo and create a feature branch.
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Run `ruff check src/ tests/` and `pytest` before pushing.
4. Open a pull request against `main`.

## License

[MIT](LICENSE)
