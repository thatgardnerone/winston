# Claude Development Context

This file provides context for Claude Code when working on homelab-brain.

## Project Overview

**Homelab Brain** is a natural language interface for homelab management, inspired by Winston from Dan Brown's *Origin*. It uses local AI (Ollama running on a GPU workstation) to answer questions about system state, provide insights, and suggest actions.

## Architecture Philosophy

1. **Test-Driven Development** - Write tests first to explore the API we want
2. **Lean Startup** - Build, measure, learn. Pivot quickly on bad ideas
3. **Type Safety** - Pydantic models for interfaces, flexible storage underneath
4. **Laravel-style Config** - Clean `config("ollama.host")` dot notation
5. **No Premature Optimization** - Start simple, add complexity only when needed

## Current State

**Phase:** PoC Development - Core functionality
**Status:** Setting up project structure, about to write first tests

### Completed
- ✅ Project structure created
- ✅ Config system (Laravel-style, auto-discovery)
- ✅ Pydantic models defined
- ✅ Dependencies specified

### Next Steps (TDD)
1. Write first test for Storage (simple key-value)
2. Implement Storage to pass test
3. Write SystemContext tests
4. Implement SystemContext
5. Mock OllamaClient + WakeOnLAN tests
6. Implement real OllamaClient
7. Wire up Brain orchestrator
8. Build CLI

## Key Design Decisions

### Storage Strategy
- **Deferred EAV**: Not implementing full EAV model yet (YAGNI)
- Start with simple dict-based storage, SQLite later if needed
- Focus on getting the API right first

### Ollama Integration
- **Wake-on-Demand**: tgoml GPU workstation sleeps by default
- Auto-wake via WakeOnLAN when query needed
- MAC: `D8:BB:C1:9B:26:93`
- Host: `http://tgoml.netbird.selfhosted:11434`
- Model: `gemma3:4b` (3.3GB, 128K context, fast on 4090)

### System Context
- Gather metrics on-demand (not continuous monitoring)
- Smart selection: only fetch context relevant to query
- Integrate with existing `homelab-health` health checker
- Cache aggressively (metrics don't change every second)

## Testing Philosophy

**Red-Green-Refactor:**
1. Write test describing ideal API
2. Watch it fail (red)
3. Write minimal code to pass (green)
4. Refactor for clarity (refactor)
5. Repeat

**Test Coverage:**
- Unit tests for individual components
- Integration tests for Brain orchestration
- Mock external dependencies (Ollama, system calls)
- Real integration tests marked with `@pytest.mark.integration`

## Code Style

- Type hints everywhere (`def ask(query: str) -> Response:`)
- Docstrings for public APIs
- Small, focused functions
- Pydantic for validation at boundaries
- Config via environment variables (12-factor app)

## Useful Commands

```bash
# Run tests
pytest                      # All tests
pytest -v                   # Verbose
pytest -k test_storage      # Specific test
pytest --cov                # With coverage

# Install deps
pip install -e ".[dev]"     # Editable install with dev deps

# Type checking (if we add mypy later)
mypy homelab_brain/
```

## Integration Points

### Existing Projects
- **homelab-health**: `/home/jamie/code/homelab-health/health_check.py`
  - Use for service/container health checks
  - Already provides JSON output
  - ~120ms execution time

### External Services
- **Ollama**: On tgoml workstation (wake-on-demand)
- **NetBird**: Mesh network for tgoml connectivity
- **WakeOnLAN**: For waking tgoml when needed

## Anti-Patterns to Avoid

❌ **Don't**: Build REST API before we need it
❌ **Don't**: Over-engineer storage (no EAV until we need it)
❌ **Don't**: Add caching/optimization before measuring
❌ **Don't**: Mock everything (real system calls are fine for integration tests)
❌ **Don't**: Write code before writing test (TDD!)

✅ **Do**: Keep it simple
✅ **Do**: Write tests that describe ideal usage
✅ **Do**: Refactor mercilessly with test coverage
✅ **Do**: Ask "do we need this yet?" before adding features

## Questions to Consider

- How do we handle ollama timeouts gracefully?
- What's the caching strategy for system metrics?
- How do we know when to wake vs when to cache?
- What's the feedback loop for AI response quality?
- How do we test WakeOnLAN without actually waking the machine?

## Agent Task Ideas

When using Claude Code agents, consider these tasks:

1. **Test Writing**: "Write tests for SystemContext CPU gathering"
2. **Implementation**: "Implement Storage class to pass existing tests"
3. **Refactoring**: "Extract prompt templates into separate module"
4. **Documentation**: "Add docstrings to all public methods"
5. **Integration**: "Connect Brain to real Ollama and test end-to-end"

## Notes

- Keep this file updated as decisions are made
- Document pivots and why we made them
- Track what worked vs what didn't (learn!)
