import sys
import unittest
from unittest.mock import patch, MagicMock
import os
# We import main inside tests to ensure mocks work correctly if imports happen at top level
from main import main

class TestMain(unittest.TestCase):
    @patch('main.LocalGitService')
    @patch('main.MockLLMService')
    @patch('main.ConsoleReportGenerator')
    @patch('main.MarkdownReportGenerator')
    @patch('main.ChronicleGenerator')
    @patch('os.path.isdir', return_value=True)
    def test_main_defaults(self, mock_isdir, mock_generator, mock_md_report, mock_console_report, mock_llm, mock_git):
        # Mock sys.argv context manager not available in 3.10 standard lib for patch.dict/object easily for list
        with patch.object(sys, 'argv', ['main.py']):
            mock_gen_instance = mock_generator.return_value
            mock_gen_instance.generate.return_value = []

            main()

            mock_git.assert_called_once_with(".")
            mock_gen_instance.generate.assert_called_once_with(limit=5)
            mock_console_report.assert_called_once()
            mock_md_report.assert_not_called()

    @patch('main.LocalGitService')
    @patch('main.MockLLMService')
    @patch('main.ConsoleReportGenerator')
    @patch('main.MarkdownReportGenerator')
    @patch('main.ChronicleGenerator')
    @patch('os.path.isdir', return_value=True)
    def test_main_custom_args(self, mock_isdir, mock_generator, mock_md_report, mock_console_report, mock_llm, mock_git):
        with patch.object(sys, 'argv', ['main.py', '/custom/repo', '-n', '10', '-f', 'markdown']):
            mock_gen_instance = mock_generator.return_value
            mock_gen_instance.generate.return_value = []

            main()

            mock_git.assert_called_once_with("/custom/repo")
            mock_gen_instance.generate.assert_called_once_with(limit=10)
            mock_md_report.assert_called_once()
            mock_console_report.assert_not_called()

    @patch('os.path.isdir', return_value=False)
    @patch('sys.stderr', new_callable=MagicMock)
    def test_main_invalid_path(self, mock_stderr, mock_isdir):
        with patch.object(sys, 'argv', ['main.py', '/invalid/path']):
            with self.assertRaises(SystemExit):
                main()
