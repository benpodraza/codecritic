# CodeCritic Contributor Guide

## Overview
- The detailed engineering specification is located at `docs/Codecritic_Spec_Plan.md`.
- Follow specification carefully for implementation tasks.

## Development Environment Setup
- Run `bash setup.sh` to install Python dependencies and tools required.
- Verify environment by running initial tests (using pytest).

## Repository Structure
- `app/`: Core system logic, including agents, managers, tools, and providers.
- `experiments/`: Experiment outputs (logs, artifacts).
- `docs/`: Project documentation and detailed specifications.

## Contribution and Style Guidelines
- Follow Python PEP8 standards strictly.
- Adhere to structured logging practices detailed in the specification.
- Write comprehensive unit tests for each functionality.

## Testing and Validation
- Unit tests: Write and run with pytest (`pytest tests/`).
- Code quality checks: Run black (`black .`), mypy (`mypy .`), radon (`radon cc .`), ruff (`ruff check .`), sonarcloud integration.
- Validate state and FSM logic carefully per detailed spec.

## PR Guidelines
- Format: `[<Phase>] <Task Description>`
- Ensure PR passes all lint, test, and code-quality checks.

## How to Use Codex for Tasks
- Always reference `docs/Codecritic_Spec_Plan.md` explicitly in prompts.
- Clearly specify exact files or modules for Codex tasks.
- Provide precise, testable acceptance criteria.

