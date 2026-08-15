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

## The live suite: when it runs, and who sees a red result

**Cadence:** every Monday at 05:13 UTC, plus on demand via *Actions → Live-Tests → Run
workflow*. See [`.github/workflows/live-tests.yml`](.github/workflows/live-tests.yml).

**Who sees it:** A red run opens an issue labelled `upstream` and the stable title “Live-Tests gegen api.srgssr.ch rot (<Datum>)”. A second red run recognises the open issue by its title prefix and appends to that same thread rather than opening a second one. Once the suite is green again, the issue closes itself.

**Three answers, not two.** `scripts/classify_live_run.py` reads the JUnit XML rather than
the exit code and separates `clear` (ran, green), `finding` (ran, something
fell) and `unknown` (did not run — install failed, nothing collected,
everything skipped). An `unknown` never closes an issue: closing would claim a
comparison that never happened.

**A red live run does not necessarily mean *our* bug.** It means the contract
with the source has changed, or the source is down. Both belong seen; only the
first belongs fixed. Please read the run before disabling the job — that is how
this check dies, and it is the only one in the repository that can contradict a
wrong assumption about api.srgssr.ch. Every other test asserts against a fixture, and
the fixture was written from the same assumption as the code.
