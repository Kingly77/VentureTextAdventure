# Contributing to Venture

Thank you for your interest in contributing! This document explains how to set up a dev environment, coding conventions, testing, and how to propose changes. If you’re just getting oriented with the codebase, also see docs/GettingStarted.md.


## Project stack at a glance
- Language: Python (CLI application)
- Package manager: pip via requirements.txt
- Testing: pytest (+ pytest-cov optional)
- Formatting: black


## Development setup
1. Fork and clone the repository.
2. Create a virtual environment and activate it:
   - Linux/macOS: `python -m venv .venv && source .venv/bin/activate`
   - Windows (PowerShell): `python -m venv .venv; .venv\Scripts\Activate.ps1`
3. Install dev dependencies:
   - `pip install -r requirements.txt`

> TODO: Document minimum supported Python version once confirmed by CI or maintainers.


## Running the game locally
From the repository root:

```bash
python game/main.py
```

By default, the engine will try to load game/worlds/default_world.json if present; otherwise it builds a starter world in code.


## Coding standards
- Use black for formatting. The repository includes black in requirements.txt.
  - Format: `black .`
  - Check only: `black --check .`
- Prefer small, focused PRs.
- Keep functions short and cohesive. Add docstrings to non-trivial classes/functions.
- Write tests for new behavior and for bug fixes.
- Avoid breaking public behavior unless there’s a strong reason; if you must, document it in CHANGELOG.md.


## Tests
- Run the full suite before opening a PR:
  - `pytest -q`
  - With coverage: `pytest --cov --cov-report=term-missing`
- If you add new modules, add corresponding tests under tests/.
- Keep tests fast and deterministic.


## Repository layout (short)
- game/ — entry point, world initialization, effects, rooms, items
- character/ — hero and enemies
- commands/ — parser, command registry, handlers
- components/ — inventory, quest log, wallet, tags
- tests/ — pytest suite
- tools/ — developer utilities

See README.md for an expanded tree.


## Working with the JSON world loader
- Schema is implemented in game/json_loader.py and related modules.
- Effect keys are registered in game/effects/registry.py.
- To add new effect types:
  1. Implement the effect behavior in game/effects/ or a suitable submodule.
  2. Register the key in game/effects/registry.py.
  3. Add tests exercising the new behavior and JSON parsing.
  4. Update README.md with the new effect key and any parameters.


## Branching, commits, and PRs
- Branch off of main: `git checkout -b feature/short-description`.
- Commit messages:
  - Short subject line (<= 72 chars)
  - Body explaining the motivation, what changed, and any side effects.
- Open a pull request:
  - Link related issues (e.g., "Fixes #123").
  - Describe testing performed and any screenshots/logs as helpful.
  - Keep PRs scoped; follow-up enhancements are welcome as separate PRs.


## Issue reporting
- Use the issue tracker and include:
  - Steps to reproduce
  - Expected vs. actual behavior
  - Environment details (OS, Python version)
  - Logs or test failures if applicable


## Code review checklist (for authors and reviewers)
- [ ] Code formatted with black
- [ ] Tests added/updated and passing locally
- [ ] README/CHANGELOG/docs updated if needed
- [ ] Minimal surface area changed (no gratuitous refactors)


## License
By contributing, you agree that your contributions will be licensed under the Apache License 2.0, consistent with the project’s LICENSE file.
