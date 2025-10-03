---
mode: agent
imports:
  - default_prompt
---

You are helping me create a new use case in strict TDD using Red, Green, Refactor steps.
Follow the rules and folder structure of my project.

### Rules:
1. **Context Selection**:
   - If I provide the context, use it.
   - If I don't, analyze the feature and propose the most appropriate context during the PLAN phase for my validation.

2. **Test Planning**:
   - Plan all the test cases upfront with their names and purposes, but do not implement them yet.
   - After planning, wait for my validation before proceeding.

3. **TDD Implementation**:
   - Implement one test at a time:
     - Write a failing test.
     - Implement the logic to make the test pass (everything in the Use Case initially).
     - Refactor only after all tests pass.
   - Use `uv pytest` to run only the tests being added at each step.

4. **Gateways**:
   - Create any required gateways in `application/gateways` during the process.
   - Use only Fake (in-memory) implementations, or Stub if Fake cannot answer the need.

5. **Fakes**:
   - Create fakes for tests in `tests/context/unit/fakes/`.

6. **Refactoring**:
   - After all tests pass, refactor the Use Case to follow clean architecture and DDD principles:
     - Introduce Commands, Responses, Services, and Domain logic as needed.

7. **Output**:
   - Ensure all tests pass at the end of the process.

### Folder Structure:
- **Use Case**: `server/src/<context>/application/use_cases/`
- **Gateways**: `server/src/<context>/application/gateways/`
- **Fakes**: `server/tests/<context>/unit/fakes/`
- **Tests**: `server/tests/<context>/unit/use_cases/`

### Steps:
1. **PLAN**:
   - Propose the context for the use case (if not provided).
   - Plan all the test cases with their names and purposes.
   - Wait for my validation before proceeding.

2. **IMPLEMENTATION**:
   - Write one failing test at a time.
   - Implement the logic to make the test pass.
   - Refactor after all tests pass.

3. **FINALIZATION**:
   - Ensure all tests pass.
   - Provide a summary of the changes made.

### Additional Rules Extracted from Examples:
- **Tests**:
  - Tests should:
    - Use pytest fixtures to inject the Use Case and fake dependencies. With conftest files if needed.
    - Follow the Arrange-Act-Assert pattern:
      - **Arrange**: Set up the fake repositories with the necessary data.
      - **Act**: Execute the Use Case.
      - **Assert**: Verify the returned data and the state of the repositories.
    - Test one logical behavior per test case.
    - Use `pytest.raises` to test exceptions.
  - Fake or Stubs only Gateways, never mock them, or anything else.

- **Use Case Implementation**:
  - Start with all logic in the Use Case file during the initial implementation.
  - Refactor to use Commands, Responses, and Services only after all tests pass.
  - Avoid unnecessary complexity in the initial implementation.

- **General**:
  - Follow the folder structure strictly.
  - Avoid comments that repeat what the code is doing.

Wait for my instructions to begin.
