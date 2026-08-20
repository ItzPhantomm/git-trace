# Contributing

GitTrace is deliberately small, local-first, and fast to start. Contributions should preserve those properties.

## Local setup

```bash
uv sync
uv run --with pytest pytest -q
```

## Contribution rules

1. Open an issue before substantial changes so the intended user problem is clear.
2. Add a focused behavior test for every code change.
3. Keep all investigation data local. The app must not require a GitHub token (public GitHub clones only).
4. Run the full test suite before opening a pull request.
5. Explain the user-visible result in the pull request description.

## Product direction

The project focuses on making unfamiliar Git history legible in seconds: what changed, who touched it, and what is currently uncommitted — for both local repositories and public GitHub URLs.