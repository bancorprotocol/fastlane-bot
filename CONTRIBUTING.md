# Contributing to fastlane-bot

Welcome and thank you for considering contributing to the fastlane-bot project! This guide will help you get started with your contributions by providing a step-by-step process on how to contribute to the project, ensuring that your contributions are consistent with our code style and standards.

## Getting Started

### 0. Preparing for Contribution

Before you start, take a moment to familiarize yourself with the fastlane-bot project:

- **Explore Open Issues**: Visit our [issues page](https://github.com/bancorprotocol/fastlane-bot/issues) to find a task. Look for issues with no assignees or those tagged as `good first issue` if you're new to the project.
- **Fork and Clone**: Fork the repository to your account and clone it locally to make your changes.
- **Environment Setup**: Make sure you have Python 3.8 or newer. Set up a virtual environment for development purposes to avoid conflicts with your other projects.

### 1. Making Changes

- **Create a Branch**: Create a new branch in your fork for your changes. This keeps your work organized and separate from the main codebase.
- **Implement Changes**: Work on the feature or fix you're contributing. Be sure to adhere to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) during development.
- **Format with Black**: Before committing, run `black .` in the project root to ensure your code is properly formatted according to our standards.
- **Test Your Code**: Add necessary tests for your changes and run `pytest` to make sure all tests pass, including yours.

### 2. Finalizing Your Contribution

- **Update Documentation**: If your changes require it, update the README.md or any relevant documentation.
- **Commit**: Use clear and concise commit messages, following the [Conventional Commits](https://www.conventionalcommits.org/) format.
- **Push and Pull Request**: Push your changes to your fork and then submit a pull request to the main repository. Link your PR to any relevant issues.

### 3. After Submission

- **Respond to Feedback**: Be prepared to respond to feedback on your pull request. The project maintainers might request changes before merging.
- **Continuous Integration Checks**: Our CI will run tests on your pull request. Ensure these checks pass.
- **Contribution Acknowledgment**: Once reviewed and approved by the maintainers, your contributions will be merged into the project.

## Contribution Guidelines

- **Code Style**: Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) and use [Black](https://github.com/psf/black) for auto-formatting. This ensures consistency and readability across the codebase.
- **Tests**: Contributions should come with tests to verify functionality and prevent regressions.
- **Documentation**: [If applicable] Update docs accordingly if your changes introduce new features or change existing ones.
- **Small PRs**: Aim to keep your pull requests small and focused on a single feature or fix for easier review.

## Issue and PR Guidelines

- **Descriptive Titles**: Use short and descriptive titles for issues and pull requests.
- **Link PRs to Issues**: Include `Fixes #<issue-number>` in your PR description to link it to the corresponding issue.
- **Use Drafts for WIP**: If your PR is a work in progress, start it as a draft to indicate it's not yet ready for review.

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md), fostering an inclusive and respectful community.

## Questions?

If you have any questions or need further guidance, feel free to open an issue with your question, and someone from the project team will be happy to assist you.

Thank you for contributing to fastlane-bot, your efforts help make the project better for everyone!
