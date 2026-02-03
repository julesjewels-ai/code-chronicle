import unittest
from src.models import Commit, AnalyzedCommit
from src.services.report import ConsoleReportGenerator, MarkdownReportGenerator

class TestReportGenerators(unittest.TestCase):
    def setUp(self):
        self.analyzed_commits = [
            AnalyzedCommit(
                commit=Commit(hash_id="123", message="test commit"),
                analysis="analysis"
            ),
            AnalyzedCommit(
                commit=Commit(hash_id="456", message="another commit"),
                analysis="more analysis"
            )
        ]

    def test_console_report(self):
        generator = ConsoleReportGenerator()
        report = generator.generate(iter(self.analyzed_commits))

        expected_fragment = "Commit 123: test commit\n  -> analysis"
        self.assertIn(expected_fragment, report)
        self.assertIn("Commit 456", report)

    def test_markdown_report(self):
        generator = MarkdownReportGenerator()
        report = generator.generate(iter(self.analyzed_commits))

        self.assertIn("# Code Evolution Narrative", report)
        self.assertIn("## Commit 123", report)
        self.assertIn("**Message:** test commit", report)
        self.assertIn("**Analysis:** analysis", report)

if __name__ == '__main__':
    unittest.main()
