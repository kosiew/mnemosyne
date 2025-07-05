# Mnemosyne Project - GEMINI.md

This document provides an overview of the Mnemosyne project, a free, open-source, spaced-repetition flashcard program. It also includes instructions for setting up the development environment, building, testing, and running the application.

## Project Overview

Mnemosyne is a spaced-repetition flashcard program designed to help users learn efficiently. It features a PyQt-based graphical user interface and uses Poetry for dependency management. The core logic for spaced repetition is located in `mnemosyne/libmnemosyne`, and `openSM2sync` handles synchronization.

## Development Setup

1.  **Python Version:** This project uses Python 3.13. It's recommended to use `pyenv` to manage Python versions.
    ```bash
    pyenv install 3.13
    pyenv local 3.13
    ```

2.  **Install Poetry:** If you don't have Poetry installed, follow the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

3.  **Install Dependencies:** Install the project dependencies using Poetry:
    ```bash
    poetry install
    ```

## Building the Project

To build the UI files and other necessary components, use the `make` command:

```bash
make build
```

This will compile the PyQt UI files (`.ui` to `ui_*.py`).

## Testing

The project uses `pytest` for testing. To run the tests, use Poetry:

```bash
poetry run pytest tests
```

For coverage reports:

```bash
poetry run coverage
```

## Linting and Formatting

The project uses `ruff` for linting and formatting.

To check for linting issues:

```bash
poetry run ruff check .
```

To automatically fix linting issues:

```bash
poetry run ruff check . --fix
```

To format the code:

```bash
poetry run ruff format .
```

## Running the Application

After building the project, you can run the Mnemosyne application:

```bash
poetry run python mnemosyne/pyqt_ui/mnemosyne
```

For debugging, you can run it with the `-d` flag:

```bash
PYTHONPATH=. poetry run python mnemosyne/pyqt_ui/mnemosyne -d dot_mnemosyne2
```
