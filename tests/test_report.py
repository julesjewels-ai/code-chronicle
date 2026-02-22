import pytest  # type: ignore
from src.models import Commit, AnalyzedCommit
from src.services.report import ConsoleReportGenerator, MarkdownReportGenerator

@pytest.fixture
def analyzed_commits():
    return [
        AnalyzedCommit(
            commit=Commit(hash_id="123", message="test commit"),
            analysis="analysis"
        ),
        AnalyzedCommit(
            commit=Commit(hash_id="456", message="another commit"),
            analysis="more analysis"
        )
    ]

def test_console_report(analyzed_commits):
    generator = ConsoleReportGenerator()
    report = generator.generate(iter(analyzed_commits))

    assert "=== Code Evolution Narrative ===" in report
    expected_fragment = "Commit 123: test commit\n  -> analysis"
    assert expected_fragment in report
    assert "Commit 456" in report
    assert "=== End of Story ===" in report

def test_markdown_report(analyzed_commits):
    generator = MarkdownReportGenerator()
    report = generator.generate(iter(analyzed_commits))

    assert "# Code Evolution Narrative" in report
    assert "## Commit 123" in report
    assert "**Message:** test commit" in report
    assert "**Analysis:** analysis" in report
