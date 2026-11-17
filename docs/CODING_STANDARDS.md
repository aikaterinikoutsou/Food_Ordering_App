# Team Coding Standards

These standards apply to Python source, tests, and Behave step definitions.
Ruff is the source of truth for Python formatting and the configured lint rules.

## Naming

- Use `PascalCase` for classes and exceptions.
- Use `snake_case` for modules, functions, methods, variables, and test names.
- Use `UPPER_SNAKE_CASE` for module-level constants.
- Prefix implementation-only helpers with `_`.
- Choose descriptive names; avoid unexplained abbreviations.
- Name tests `test_<behavior>` and keep each test focused on one behavior.

## Formatting and imports

- Use four spaces for indentation; do not use tabs.
- Keep lines to 88 characters or fewer.
- Use double quotes for Python strings unless escaping makes another quote style
  clearer.
- Separate top-level definitions with two blank lines and methods with one blank
  line.
- Put imports at the top of the file, grouped and sorted as standard library,
  third-party, then local imports. Ruff enforces import ordering.
- Let `ruff format` handle consistent formatting; do not hand-format around it.

## Code and project structure

- Keep domain data and behavior in `src/models.py`, service rules and external
  boundaries in `src/services.py`, application workflows in
  `src/application.py`, terminal interaction in `src/cli.py`, seeded demo data
  in `src/demo_data.py`, and JSON persistence in `src/session_store.py`.
- Put automated tests under `test/`; put Gherkin specifications and their
  Behave steps under `validation/features/`.
- Add type annotations to new public functions and methods. Prefer explicit
  domain types and clear return values.
- Keep functions focused and changes scoped to the feature being implemented.
- Raise meaningful errors for invalid operations; do not silently swallow
  failures or return success-shaped fallbacks.
- Keep external integrations explicit. Current payment, notification, menu
  availability, and GPS behavior is simulated and must not be described as a
  live integration.
- Add or update tests when behavior changes. Update directly related
  documentation when the workflow or project usage changes.

## Commits

- Use Conventional Commit subjects:
  `<type>(optional-scope): imperative summary`
- Common types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `build`,
  and `chore`.
- Keep the subject concise, imperative, and under 72 characters; do not end it
  with a period.
- Examples: `feat(cart): persist cart between sessions`,
  `fix(checkout): reject unavailable items`, `docs: add project context`.
- Describe the reason and any user-visible behavior in the commit body when the
  subject alone is insufficient.

## Required checks

Run these checks before submitting changes:

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest
python -m behave --format progress
```

Apply the Ruff auto-fixes and formatter with:

```powershell
python -m ruff check --fix .
python -m ruff format .
```

Ruff's configured lint rules check common Python errors and import ordering;
the formatter enforces the configured line length, quotes, and indentation.
Naming, structure, type annotations, tests, and commit message conventions are
team review standards and should be followed alongside the automated checks.
