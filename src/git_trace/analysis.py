"""Git Trace — terminal forensics for Git repositories (local and GitHub URLs)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile


@dataclass(frozen=True)
class FileActivity:
    path: str
    touches: int


@dataclass(frozen=True)
class Commit:
    short_hash: str
    author: str
    relative_date: str
    subject: str


@dataclass(frozen=True)
class Investigation:
    repository: Path
    branch: str
    commit_count: int
    author_count: int
    dirty_files: tuple[str, ...]
    hot_files: tuple[FileActivity, ...]
    recent_commits: tuple[Commit, ...]


GITHUB_URL_PATTERN = re.compile(
    r"^(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)(?:\.git)?/?$"
)
GITHUB_SHORT_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$")


def _git(repository: Path, *args: str, strip: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError("Path is not a Git repository")
    return result.stdout.strip() if strip else result.stdout


def _clone_github_url(owner: str, repo: str, cache_dir: Path) -> Path:
    """Clone a GitHub repository to cache directory, or return existing cached path."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / f"{owner}-{repo}"

    if target.exists():
        # Update existing clone
        _git(target, "fetch", "--all", "--quiet")
        _git(target, "reset", "--hard", "origin/HEAD", "--quiet")
        return target

    # Shallow clone for speed
    result = subprocess.run(
        ["git", "clone", "--depth", "50", "--quiet", f"https://github.com/{owner}/{repo}.git", str(target)],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        # Try full clone if shallow fails (e.g., very small repos)
        shutil.rmtree(target, ignore_errors=True)
        result = subprocess.run(
            ["git", "clone", "--quiet", f"https://github.com/{owner}/{repo}.git", str(target)],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise ValueError(f"Failed to clone {owner}/{repo}: {result.stderr}")
    return target


def resolve_repository(path_or_url: str | Path) -> Path:
    """Resolve a local path or GitHub URL to a local repository path.

    Supported formats:
    - Local path: /path/to/repo or ./repo
    - GitHub HTTPS: https://github.com/owner/repo
    - GitHub short: github.com/owner/repo
    - GitHub shorthand: owner/repo

    Uses GIT_TRACE_CACHE_DIR env var or ~/.cache/git-trace for cloned repos.
    """
    path = Path(path_or_url).expanduser()

    # Check if it's a local path first
    if path.exists():
        _git(path, "rev-parse", "--git-dir")
        return path.resolve()

    # Check if it's a GitHub URL or shorthand
    path_str = str(path_or_url)

    # Full GitHub URL
    match = GITHUB_URL_PATTERN.match(path_str)
    if match:
        owner, repo = match.groups()
        cache_dir = Path(os.environ.get("GIT_TRACE_CACHE_DIR", Path.home() / ".cache" / "git-trace"))
        return _clone_github_url(owner, repo, cache_dir)

    # Short form: owner/repo
    match = GITHUB_SHORT_PATTERN.match(path_str)
    if match:
        owner, repo = match.groups()
        cache_dir = Path(os.environ.get("GIT_TRACE_CACHE_DIR", Path.home() / ".cache" / "git-trace"))
        return _clone_github_url(owner, repo, cache_dir)

    raise ValueError(
        f"'{path_or_url}' is not a valid local Git repository path or GitHub URL. "
        "Supported formats: local path, https://github.com/owner/repo, github.com/owner/repo, owner/repo"
    )


def investigate(path_or_url: str | Path) -> Investigation:
    repository = resolve_repository(path_or_url)

    log_lines = _git(repository, "log", "--pretty=format:%h\x1f%an\x1f%ar\x1f%s", "--name-only").splitlines()
    commits: list[Commit] = []
    file_touches: Counter[str] = Counter()
    for line in log_lines:
        if "\x1f" in line:
            short_hash, author, relative_date, subject = line.split("\x1f", maxsplit=3)
            commits.append(Commit(short_hash, author, relative_date, subject))
        elif line:
            file_touches[line] += 1

    dirty_files = tuple(
        line[3:] if len(line) > 3 else line
        for line in _git(repository, "status", "--porcelain", strip=False).splitlines()
        if line
    )
    hot_files = tuple(
        FileActivity(file, touches)
        for file, touches in file_touches.most_common(8)
    )
    return Investigation(
        repository=repository,
        branch=_git(repository, "branch", "--show-current") or "detached HEAD",
        commit_count=len(commits),
        author_count=len({commit.author for commit in commits}),
        dirty_files=dirty_files,
        hot_files=hot_files,
        recent_commits=tuple(commits[:12]),
    )