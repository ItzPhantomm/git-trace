# Git Crime Scene

> Turn an unfamiliar Git repository into a readable case file in seconds.

**Git Crime Scene** is a fast, local-first terminal dashboard that answers the questions every maintainer asks when opening a repo: **what changed, who touched it most, and what evidence is still uncommitted?**

No account. No token. No cloud upload. Point it at a repository and investigate.

## Why this exists

`git log`, `git blame`, and `git status` are excellent tools—but they make you assemble the story yourself. Git Crime Scene gives you the first forensic pass in one focused screen:

- **Case file:** branch, commit count, contributor count, and working-tree state
- **Most disturbed files:** the paths repeatedly touched throughout the repository’s history
- **Recent activity:** a concise commit timeline with author and relative time
- **Uncommitted clues:** immediate visibility into active local changes

It is built for onboarding, incident triage, inherited codebases, and the moment somebody asks: “What happened here?”

## Install

### Fastest: run directly from GitHub

```bash
uvx --from git+https://github.com/ItzPhantomm/git-crime-scene.git crime-scene /path/to/repository
```

### Persistent install

```bash
uv tool install git+https://github.com/ItzPhantomm/git-crime-scene.git
crime-scene /path/to/repository
```

### From source

```bash
git clone https://github.com/ItzPhantomm/git-crime-scene.git
cd git-crime-scene
uv sync
uv run crime-scene /path/to/repository
```

**Requirements:** Git and Python 3.11+ (or `uv`).

## Use it

```bash
crime-scene ~/code/my-project
```

Inside the dashboard:

| Key | Action |
| --- | --- |
| `r` | Refresh the current investigation |
| `q` | Quit |
| `Enter` in the path field | Investigate another repository |

## Local-first by design

Git Crime Scene reads only the local repository you select. It does not require GitHub credentials, network access, telemetry, or a hosted service.

## Development

```bash
uv sync
uv run --with pytest pytest -q
```

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the local setup, testing contract, and product direction.

## License

[MIT](LICENSE)
