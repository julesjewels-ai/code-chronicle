import unittest
from unittest.mock import patch
import sys
import os

# Ensure we can import main
sys.path.append(os.getcwd())
from main import main, parse_args

class TestCLI(unittest.TestCase):

    def test_parse_args_defaults(self):
        with patch('sys.argv', ['main.py']):
            args = parse_args()
            self.assertEqual(args.path, ".")
            self.assertEqual(args.limit, 5)
            self.assertEqual(args.format, "console")

    def test_parse_args_full(self):
        with patch('sys.argv', ['main.py', '-n', '10', '-f', 'markdown', '/tmp']):
            args = parse_args()
            self.assertEqual(args.path, '/tmp')
            self.assertEqual(args.limit, 10)
            self.assertEqual(args.format, 'markdown')

    @patch('main.ChronicleGenerator')
    @patch('main.LocalGitService')
    @patch('main.MockLLMService')
    @patch('main.ConsoleReportGenerator')
    @patch('main.MarkdownReportGenerator')
    @patch('os.path.isdir')
    @patch('sys.exit')
    def test_main_success_console(self, mock_exit, mock_isdir, mock_md_report, mock_console_report, mock_llm, mock_git, mock_generator):
        # Setup
        mock_isdir.return_value = True

        mock_gen_instance = mock_generator.return_value
        mock_gen_instance.generate.return_value = []

        mock_report_instance = mock_console_report.return_value
        mock_report_instance.generate.return_value = "Story"

        with patch('sys.argv', ['main.py', '.']):
            # Run
            main()

        # Assertions
        mock_isdir.assert_called_with(".")
        mock_git.assert_called_with(".")
        mock_console_report.assert_called_once()
        mock_md_report.assert_not_called()
        mock_gen_instance.generate.assert_called_with(limit=5)
        mock_report_instance.generate.assert_called()

    @patch('main.ChronicleGenerator')
    @patch('main.LocalGitService')
    @patch('main.MockLLMService')
    @patch('main.ConsoleReportGenerator')
    @patch('main.MarkdownReportGenerator')
    @patch('os.path.isdir')
    def test_main_success_markdown(self, mock_isdir, mock_md_report, mock_console_report, mock_llm, mock_git, mock_generator):
        # Setup
        mock_isdir.return_value = True

        # Setup mocks to return iterables/strings where needed to prevent errors if main() uses them
        mock_gen_instance = mock_generator.return_value
        mock_gen_instance.generate.return_value = []

        mock_report_instance = mock_md_report.return_value
        mock_report_instance.generate.return_value = "Markdown Story"

        with patch('sys.argv', ['main.py', '-f', 'markdown', 'custom_repo']):
            # Run
            main()

        # Assertions
        mock_isdir.assert_called_with("custom_repo")
        mock_git.assert_called_with("custom_repo")
        mock_md_report.assert_called_once()
        mock_console_report.assert_not_called()

    @patch('os.path.isdir')
    @patch('sys.exit')
    def test_main_invalid_path(self, mock_exit, mock_isdir):
        # Setup
        mock_isdir.return_value = False

        with patch('sys.argv', ['main.py', '/bad/path']):
            # Run
            main()

        # Assertions
        mock_exit.assert_called_with(1)

if __name__ == '__main__':
    unittest.main()
