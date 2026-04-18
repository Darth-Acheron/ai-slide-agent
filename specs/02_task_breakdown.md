# 02 Task Breakdown

## Core Goal: 
Use GLM-5.1 to check the specifications (`specs/01_system_architecture_and_design.md`) and the current code (`web/app.py`, `web/templates/index.html`) to ensure alignment, identify bugs or bad practices, and then write and run tests for the application.

## Tasks:
1. Initialize the SDD structure (Completed).
2. Generate Specs from the current codebase (Completed).
3. Send the source code and the specs to GLM-5.1 via the Ali Bailian API.
4. Extract GLM-5.1's code review feedback.
5. Create a test script (`tests/test_app.py`) based on the spec/implementation or GLM's suggestions.
6. Execute the test script using `pytest` and fix any issues discovered.