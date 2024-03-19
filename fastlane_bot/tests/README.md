# Fastlane Bot Testing Infrastructure

This document outlines the testing infrastructure for the `fastlane-bot` library.

## Overview

The `fastlane-bot` library employs the pytest framework for its testing needs. This framework provides a robust and flexible platform for developing and executing tests, ensuring the reliability and quality of the library.

## Test Data

- All data required for tests should be stored in the directory: `fastlane_bot/tests/_data`.

## Legacy Testing Resources

- Jupyter Notebook styled legacy testing resources should be contained within `resources/`.
- Only optimizer-related tests, which test code found in `fastlane_bot/tools/*`, should continue to use the Jupyter Notebook styled legacy testing framework.

## Pytest Script-Based Framework

- All other functionality should maintain tests using the traditional pytest script-based framework.
- These tests should be stored in: `fastlane_bot/tests`.

## GitHub Actions

- GitHub Actions are set up to run the bash script called `run_tests`. This script is found at the top level of the project directory.
- The `run_tests` script generates pytest scripts from the .py files found in `resources/NBTest/*`. These generated pytest scripts are then written to `fastlane_bot/tests/nbtest/`.

## Running Tests

- All tests are run using the following command:
  ```bash
  ./run_tests
  ```
