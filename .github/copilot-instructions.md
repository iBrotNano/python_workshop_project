# Copilot Instructions (Python)

## Python Environment
- Assume the workspace interpreter is already configured.
- Do not call interpreter/environment setup tools unless the user explicitly asks.
- Only re-check environment if Python execution fails with missing interpreter or missing module errors.

## General
- Prefer small, readable functions and clear naming.
- Keep changes minimal and focused on the request.
- Keep your answers concise and to the point.

## Project Structure
- Source code lives in the `src/` directory.
- Tests live in the `tests/` directory.
- Every class has its own file named after the class in snake_case. For example, a class named `MyClass` would be in a file named `my_class.py`.

## Testing
- Use `pytest` as the test framework.
- Name tests `test_*.py` and test functions `test_*`.
- No comments in tests, the test name should be descriptive enough.
- Keep tests as they are and only modify them to fix a bug or add coverage for new code.
- Either change tests or code, but not both at the same time. It is not possible that a system validates or falsifies itself.

## Style
- Prefer explicit imports.
- Avoid wildcard imports.
- Start private fields and methods with a double underscore (__).
- Use snake_case for functions and variables, and PascalCase for classes.
- Add type hints for function parameters and return types. Only add None as return type hint if it is returned explicitly. If the function does not return anything, it is not necessary to add a return type hint.
- Use f-strings for string formatting.

## Documentation

- Add brief comments only when the intent is not obvious.
- Use docstrings to document functions, classes, and modules.
- Encapsulate the docstring in triple quotes (""" """).
- The triple quotes are on own lines. The comment between them.
- The language the documentation is written is English.
- Add :param param_name: description for each parameter in the docstring. Except for parameter self for classes.
- Add :type param_name: type for each parameter in the docstring except for the parameter self.
- Add :return: description for the return value in the docstring.
- Add :rtype: type for the return value in the docstring.
- Add :raises ExceptionType: description for each exception that can be raised in the function.
- Document all properties of classes decorated with @dataclass
