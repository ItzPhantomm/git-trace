from __future__ import annotations

import argparse
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Static

from .analysis import Investigation, investigate

MOCHA = """
Screen { background: #1e1e2e; color: #cdd6f4; }
Header { background: #181825; color: #cba6f7; }
Footer { background: #181825; color: #a6adc8; }
#hero { height: 7; padding: 1 3; background: #313244; border: tall #cba6f7; margin: 1 2 0 2; }
#title { color: #cba6f7; text-style: bold; }
#subtitle { color: #a6adc8; }
#controls { height: 5; padding: 1 2; margin: 0 2; }
Input { width: 1fr; border: tall #45475a; background: #181825; color: #cdd6f4; }
Input:focus { border: tall #89b4fa; }
Button { margin-left: 1; background: #cba6f7; color: #1e1e2e; text-style: bold; }
#case-summary { margin: 0 2 1 2; padding: 1 2; color: #a6e3a1; background: #181825; border: tall #45475a; }
.panel { width: 1fr; height: 1fr; margin: 0 1 1 1; padding: 1; background: #181825; border: tall #45475a; }
.panel-title { color: #89b4fa; text-style: bold; margin-bottom: 1; }
DataTable { height: 1fr; background: #181825; color: #cdd6f4; }
#clues { color: #f9e2af; height: 1fr; }
"""


def build_case_summary(report: Investigation) -> str:
    clue_word = "clue" if len(report.dirty_files) == 1 else "clues"
    lead_file = report.hot_files[0].path if report.hot_files else "no file history"
    return (
        f"CASE FILE  ·  {report.branch}  ·  {report.commit_count} commits  ·  "
        f"{report.author_count} suspects  ·  {len(report.dirty_files)} uncommitted {clue_word}  ·  "
        f"lead evidence: {lead_file}"
    )


class CrimeScene(App[None]):
    TITLE = "Git Crime Scene"
    SUB_TITLE = "Repository forensics"
    CSS = MOCHA
    BINDINGS = [("r", "refresh_case", "Refresh"), ("q", "quit", "Quit")]

    def __init__(self, repository: str | Path = ".") -> None:
        super().__init__()
        self.repository = Path(repository).resolve()
        self.report: Investigation | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="hero"):
            yield Label("GIT CRIME SCENE", id="title")
            yield Label("Trace the fingerprints your repository left behind.", id="subtitle")
        with Horizontal(id="controls"):
            yield Input(value=str(self.repository), placeholder="Repository path", id="repository")
            yield Button("Investigate", id="investigate", variant="primary")
        yield Static("Loading case file…", id="case-summary")
        with Horizontal():
            with Container(classes="panel"):
                yield Label("MOST DISTURBED FILES", classes="panel-title")
                yield DataTable(id="hot-files")
            with Container(classes="panel"):
                yield Label("RECENT ACTIVITY", classes="panel-title")
                yield DataTable(id="timeline")
            with Container(classes="panel"):
                yield Label("UNCOMMITTED CLUES", classes="panel-title")
                yield VerticalScroll(Static(id="clues"))
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#hot-files", DataTable).add_columns("File", "Touches")
        self.query_one("#timeline", DataTable).add_columns("Commit", "Who", "When", "What happened")
        self.load_case()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "investigate":
            self.load_case()

    def on_input_submitted(self, _: Input.Submitted) -> None:
        self.load_case()

    def action_refresh_case(self) -> None:
        self.load_case()

    def load_case(self) -> None:
        requested_path = self.query_one("#repository", Input).value
        try:
            self.report = investigate(requested_path)
        except ValueError as error:
            self.query_one("#case-summary", Static).update(f"CASE CLOSED  ·  {error}")
            return

        report = self.report
        self.repository = report.repository
        self.query_one("#repository", Input).value = str(report.repository)
        self.query_one("#case-summary", Static).update(build_case_summary(report))

        hot_files = self.query_one("#hot-files", DataTable)
        hot_files.clear()
        for evidence in report.hot_files:
            hot_files.add_row(evidence.path, str(evidence.touches))

        timeline = self.query_one("#timeline", DataTable)
        timeline.clear()
        for commit in report.recent_commits:
            timeline.add_row(commit.short_hash, commit.author, commit.relative_date, commit.subject)

        clues = "\n".join(f"• {path}" for path in report.dirty_files) or "No active evidence. Working tree is clean."
        self.query_one("#clues", Static).update(clues)


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive Git repository forensics")
    parser.add_argument("repository", nargs="?", default=".", help="Path to a Git repository")
    args = parser.parse_args()
    CrimeScene(args.repository).run()


if __name__ == "__main__":
    main()
