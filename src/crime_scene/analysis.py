from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import subprocess


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


def investigate(path: str | Path) -> Investigation:
    repository = Path(path).resolve()
    _git(repository, "rev-parse", "--git-dir")

    log_lines = _git(repository, "log", "--pretty=format:%h%x1f%an%x1f%ar%x1f%s", "--name-only").splitlines()
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
