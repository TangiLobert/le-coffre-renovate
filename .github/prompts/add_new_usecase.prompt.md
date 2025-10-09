---
mode: agent
imports:
  - default_back
---

You are helping me create a new use case using strict TDD (Red, Green, Refactor).

### Rules:

1. **Context Selection**:
   - If I provide the context, use it
   - If not, analyze the feature and propose the most appropriate context during PLAN for validation

2. **Test Planning**:
   - Plan all test cases upfront with names and purposes only
   - They should follow Given-When-Then format strictly
   - Wait for my validation before implementation

3. **TDD Implementation**:
   - One test at a time: Red → Green → Refactor (only after ALL tests pass)
   - Write failing test → Implement minimal logic in use case only → Next test
   - Use `uv pytest <specific_test_file>` to run current tests
   - Follow Arrange-Act-Assert pattern
   - Test one logical behavior per test case
   - Use pytest fixtures for dependency injection

4. **Use Case Structure**:
   - Class with `__init__(dependencies)` for DI
   - `execute(command)` method that returns a result
   - No imports outside `<context>/application`, `<context>/domain` or `shared_kernel`
   - Confirm if `shared_kernel` imports needed during PLAN
   - No redundant comments

5. **Dependencies**:
   - Create gateways in `application/gateways/`
   - Create fakes in `tests/<context>/unit/fakes/`
   - Use Fake (in-memory) or Stub implementations only

6. **Refactoring (after ALL tests pass)**:
   - Extract Commands, Responses, Services, Domain logic as needed
   - Follow clean architecture and DDD principles

### Process:
1. **PLAN**: Propose context + list test cases + Gateways involved → wait for validation
2. **IMPLEMENT**: TDD cycle for each test → refactor when all pass
3. **FINALIZE**: Ensure all tests pass + summary

Wait for instructions.
