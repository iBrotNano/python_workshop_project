# Copilot Instructions (Python)

## General
- Prefer small, readable functions and clear naming.
- Keep changes minimal and focused on the request.

## Project Structure
- Source code lives in the `src/` directory.
- Tests live in the `tests/` directory.

## Testing
- Use `pytest` as the test framework.
- Name tests `test_*.py` and test functions `test_*`.
- No comments in tests, the test name should be descriptive enough.
- Don't change existing tests unless necessary to fix a bug or add coverage for new code.
- Either change tests or code, but not both at the same time. It is not possible that a system validates or falsifies itself.

## Style
- Prefer explicit imports and avoid wildcard imports.

## Documentation

- Add brief comments only when the intent is not obvious.
- Use docstrings to document functions, classes, and modules.
- Use type hints for function parameters and return types.
- The language the documentation is written is English.
