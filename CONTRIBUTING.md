# Contributing to swiss-democracy-mcp

[🇩🇪 Deutsche Version](CONTRIBUTING.de.md)

Thank you for your interest in contributing! This server is part of the [Swiss Public Data MCP Portfolio](https://github.com/malkreide/swiss-public-data-mcp).

## Development Setup

```bash
git clone https://github.com/malkreide/swiss-democracy-mcp.git
cd swiss-democracy-mcp
pip install -e ".[dev]"
```

## Running Tests

```bash
# Unit tests only (no network, fast)
PYTHONPATH=src pytest tests/ -m "not live" -v

# All tests including live API calls
PYTHONPATH=src pytest tests/ -v
```

## Code Style

This project uses [ruff](https://docs.astral.sh/ruff/) for linting:

```bash
python -m ruff check src/ tests/
python -m ruff check src/ tests/ --fix
```

## Adding New Tools

1. Define a Pydantic input model (Pydantic v2, `model_config = ConfigDict(extra="forbid")`)
2. Implement an `async def` tool function with `@mcp.tool(name=..., annotations=...)`
3. Write a comprehensive docstring with Args/Returns sections
4. Add unit tests with `respx` mocking for HTTP calls
5. Mark live tests with `@pytest.mark.live`

## Data Source Notes

- **Swissvotes CSV** — 874 columns, semicolon-delimited, BOM-prefixed. Loaded once at startup and cached 24h. Column names follow the Swissvotes codebook: https://swissvotes.ch/page/dataset
- **BFS opendata.swiss** — CKAN API, no auth. Package IDs are stable.
- **SRGSSR Polis** — OAuth2 client credentials. Tokens are cached in memory.

## Pull Requests

Please open an issue first for significant changes. PRs should include tests and pass `ruff` linting.
