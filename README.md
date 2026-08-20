# GitTrace

> Trace Git history — local repositories and GitHub URLs — in a premium terminal dashboard.

**GitTrace** is a fast, local-first terminal dashboard that answers the questions every maintainer asks when opening a repo: **what changed, who touched it most, and what evidence is still uncommitted?**

No account. No token. No cloud upload. Point it at a local repository or a GitHub URL and investigate.

## Why this exists

`git log`, `git blame`, and `git status` are excellent tools—but they make you assemble the story yourself. GitTrace gives you the first forensic pass in one focused screen:

- **Trace file:** branch, commit count, contributor count, and working-tree state
- **Most touched files:** the paths repeatedly touched throughout the repository's history
- **Recent commits:** a concise commit timeline with author and relative time
- **Uncommitted changes:** immediate visibility into active local changes

It is built for onboarding, incident triage, inherited codebases, and the moment somebody asks: "What happened here?"

## Install

### Fastest: run directly from GitHub

```bash
uvx --from git+https://github.com/ItzPhantomm/git-trace.git git-trace /path/to/repository
```

### Fastest with GitHub URL

```bash
uvx --from git+https://github.com/ItzPhantomm/git-trace.git git-trace ItzPhantomm/git-trace
```

### Persistent install

```bash
uv tool install git+https://github.com/ItzPhantomm/git-trace.git
git-trace /path/to/repository
# or
git-trace owner/repo
```

### From source

```bash
git clone https://github.com/ItzPhantomm/git-trace.git
cd git-trace
uv sync
uv run git-trace /path/to/repository
```

**Requirements:** Git and Python 3.11+ (or `uv`).

## Use it

### Local repository

```bash
git-trace ~/code/my-project
```

### GitHub repository (shorthand)

```bash
git-trace ItzPhantomm/git-trace
```

### GitHub repository (full URL)

```bash
git-trace https://github.com/ItzPhantomm/git-trace
git-trace github.com/ItzPhantomm/git-trace
```

### Inside the dashboard

| Key | Action |
| --- | --- |
| `r` | Refresh the current trace |
| `q` | Quit |
| `Enter` in the input field | Trace another repository |

GitHub repositories are cloned to `~/.cache/git-trace` (or `$GIT_TRACE_CACHE_DIR`) and updated on subsequent runs.

## Local-first by design

GitTrace reads only the local repository you select. It does not require GitHub credentials, network access beyond cloning public repositories, telemetry, or a hosted service.

## Development

```bash
uv sync
uv run --with pytest pytest -q
```

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the local setup, testing contract, and product direction.

## License

[MIT](LICENSE)