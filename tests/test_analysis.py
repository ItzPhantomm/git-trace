from __future__ import annotations

import subprocess
from pathlib import Path

from crime_scene.analysis import investigate


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "evidence"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "detective@example.test")
    git(repo, "config", "user.name", "Detective")
    return repo


def commit(repo: Path, filename: str, content: str, message: str) -> None:
    (repo / filename).write_text(content)
    git(repo, "add", filename)
    git(repo, "commit", "-qm", message)


def test_investigate_counts_commits_authors_and_changed_files(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit(repo, "app.py", "print('first')\n", "Create application")
    commit(repo, "app.py", "print('second')\n", "Change application")

    report = investigate(repo)

    assert report.commit_count == 2
    assert report.author_count == 1
    assert report.hot_files[0].path == "app.py"
    assert report.hot_files[0].touches == 2
    assert report.recent_commits[0].subject == "Change application"


def test_investigate_reports_uncommitted_evidence(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit(repo, "README.md", "# Case\n", "Open case")
    (repo / "README.md").write_text("# Case\nUncommitted clue\n")

    report = investigate(repo)

    assert report.dirty_files == ("README.md",)


def test_investigate_rejects_non_repository_paths(tmp_path: Path) -> None:
    try:
        investigate(tmp_path)
    except ValueError as error:
        assert "Git repository" in str(error)
    else:
        raise AssertionError("Expected a non-repository path to be rejected")
