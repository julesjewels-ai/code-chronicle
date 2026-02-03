from collections.abc import Iterator
from ..interfaces import ReportGenerator
from ..models import AnalyzedCommit

class ConsoleReportGenerator(ReportGenerator):
    def generate(self, analyzed_commits: Iterator[AnalyzedCommit]) -> str:
        return "\n\n".join(
            f"Commit {ac.commit.hash_id}: {ac.commit.message}\n  -> {ac.analysis}"
            for ac in analyzed_commits
        )

class MarkdownReportGenerator(ReportGenerator):
    def generate(self, analyzed_commits: Iterator[AnalyzedCommit]) -> str:
        lines = ["# Code Evolution Narrative", ""]
        for ac in analyzed_commits:
            lines.append(f"## Commit {ac.commit.hash_id}")
            lines.append(f"**Message:** {ac.commit.message}")
            lines.append(f"**Analysis:** {ac.analysis}")
            lines.append("")
        return "\n".join(lines)
