import unittest
from unittest.mock import patch, MagicMock
import subprocess
from src.services.git import LocalGitService
from src.models import Commit

class TestLocalGitService(unittest.TestCase):
    def setUp(self):
        self.service = LocalGitService("/path/to/repo")

    @patch("subprocess.run")
    def test_get_commit_history_success(self, mock_run):
        # Setup mock return value
        mock_result = MagicMock()
        mock_result.stdout = "abc1234|First commit\ndef5678|Second commit"
        mock_run.return_value = mock_result

        commits = self.service.get_commit_history(2)

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].hash_id, "abc1234")
        self.assertEqual(commits[0].message, "First commit")
        self.assertEqual(commits[1].hash_id, "def5678")
        self.assertEqual(commits[1].message, "Second commit")

        # Verify call
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        self.assertIn("git", args[0])
        self.assertIn("-n", args[0])
        self.assertIn("2", args[0])

    @patch("subprocess.run")
    def test_get_commit_history_empty(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        commits = self.service.get_commit_history(5)
        self.assertEqual(commits, [])

    @patch("subprocess.run")
    def test_get_commit_history_parsing_error_handling(self, mock_run):
        # Test malformed lines are skipped
        mock_result = MagicMock()
        mock_result.stdout = "abc1234|Good commit\nbad_line_no_pipe\n1234567|Another good one"
        mock_run.return_value = mock_result

        commits = self.service.get_commit_history(3)

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].message, "Good commit")
        self.assertEqual(commits[1].message, "Another good one")

    @patch("subprocess.run")
    def test_get_commit_history_subprocess_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "git log")

        # Capture stdout to verify print behavior
        with patch('builtins.print') as mock_print:
            commits = self.service.get_commit_history(1)
            mock_print.assert_called_once()
            self.assertIn("Error fetching git log", mock_print.call_args[0][0])

        self.assertEqual(commits, [])
