# GitHub Copilot Instruction for Mnemosyne Repository

## Overview
This repository contains the Mnemosyne project, a spaced repetition software. The repository includes Python scripts, database management, and a variety of tools for managing and analyzing spaced repetition data. The project uses `typer` for CLI commands and SQLite for database operations.

## Guidelines for Using GitHub Copilot

### General Coding Practices
- **Follow PEP 8**: Ensure all Python code adheres to PEP 8 standards.
- **Type Annotations**: Use type annotations for all function arguments and return types.
- **Docstrings**: Add clear and concise docstrings for all functions and classes.
- **Error Handling**: Implement proper error handling, especially for database operations and file I/O.

### Database Operations
- **SQL Queries**: Use parameterized queries to prevent SQL injection.
- **Database Connections**: Always close database connections after operations.
- **Backups**: Ensure database backup and restore functionalities are robust and tested.

### CLI Commands
- **Typer Usage**: Use `typer` for creating CLI commands. Ensure commands have clear help messages and default values where applicable.
- **Command Testing**: Test all CLI commands for edge cases and invalid inputs.

### File Structure
- **Modular Code**: Keep the code modular. Avoid adding unrelated functionalities to existing scripts.
- **Documentation**: Update `README.md` and other documentation files when adding new features or modifying existing ones.

### Testing
- **Unit Tests**: Write unit tests for all new features and bug fixes.
- **Test Coverage**: Aim for high test coverage, especially for critical components like database operations and CLI commands.
- **Benchmarking**: Use the `tests/benchmark_*.py` scripts for performance testing when applicable.

### Commit Messages
- **Descriptive Messages**: Write descriptive commit messages that explain the purpose of the changes.
- **Issue References**: Reference related issues or pull requests in commit messages when applicable.

### Pull Requests
- **Code Reviews**: Ensure all pull requests are reviewed by at least one other contributor.
- **Linting and Tests**: Pass all linting checks and tests before submitting a pull request.
- **Changelogs**: Update the `ChangeLog` file with a summary of changes when submitting a pull request.

### Security
- **Sensitive Data**: Do not hardcode sensitive data like database credentials or API keys.
- **Dependencies**: Regularly update dependencies and check for vulnerabilities.

### Localization
- **Translation Files**: Update `.po` files in the `po/` directory when adding or modifying user-facing text.
- **Consistency**: Ensure translations are consistent across all languages.

## Copilot-Specific Instructions
- **Code Suggestions**: Use Copilot to generate boilerplate code, but always review and test the suggestions.
- **Documentation**: Use Copilot to draft documentation, but ensure it aligns with the project's style and standards.
- **Testing**: Leverage Copilot to generate test cases, but validate them for correctness and coverage.

## Additional Notes
- **Community Contributions**: Encourage community contributions by providing clear guidelines in `CONTRIBUTING.md`.
- **Issue Tracking**: Use GitHub Issues to track bugs, feature requests, and other tasks.

By following these guidelines, we can ensure the Mnemosyne project remains maintainable, secure, and user-friendly.
