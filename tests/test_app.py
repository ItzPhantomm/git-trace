from pathlib import Path

from crime_scene.analysis import Commit, FileActivity, Investigation
from crime_scene.app import build_case_summary


def test_case_summary_surfaces_high_value_repository_evidence() -> None:
    report = Investigation(
        repository=Path("/cases/demo"),
        branch="main",
        commit_count=42,
        author_count=3,
        dirty_files=("config.yaml",),
        hot_files=(FileActivity("src/app.py", 8),),
        recent_commits=(Commit("a1b2c3d", "Ada", "2 hours ago", "Fix auth"),),
    )

    summary = build_case_summary(report)

    assert "42 commits" in summary
    assert "3 suspects" in summary
    assert "1 uncommitted clue" in summary
    assert "src/app.py" in summary
