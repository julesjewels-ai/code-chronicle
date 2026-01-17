import unittest
from unittest.mock import MagicMock, patch
from src.services.git import LocalGitService
from src.models import Commit
import subprocess

class TestLocalGitService(unittest.TestCase):
    def setUp(self):
        self.service = LocalGitService("/tmp/repo")

    def test_parse_git_log_valid(self):
        output = "hash1|message1\nhash2|message2"
        expected = [
            Commit(hash_id="hash1", message="message1"),
            Commit(hash_id="hash2", message="message2")
        ]
        result = self.service._parse_git_log(output)
        self.assertEqual(result, expected)

    def test_parse_git_log_with_empty_lines(self):
        output = "\n\nhash1|message1\n\n"
        expected = [
            Commit(hash_id="hash1", message="message1")
        ]
        result = self.service._parse_git_log(output)
        self.assertEqual(result, expected)

    def test_parse_git_log_malformed(self):
        # Lines without '|' should be ignored based on current implementation
        output = "hash1|message1\nmalformed_line\nhash2|message2"
        expected = [
            Commit(hash_id="hash1", message="message1"),
            Commit(hash_id="hash2", message="message2")
        ]
        result = self.service._parse_git_log(output)
        self.assertEqual(result, expected)

    def test_parse_git_log_extra_separator(self):
        # Should split only on first '|'
        output = "hash1|message|with|pipes"
        expected = [
            Commit(hash_id="hash1", message="message|with|pipes")
        ]
        result = self.service._parse_git_log(output)
        self.assertEqual(result, expected)

    def test_parse_git_stream(self):
        # Test the new streaming parser directly
        stream = ["hash1|message1\n", "hash2|message2"]
        expected = [
            Commit(hash_id="hash1", message="message1"),
            Commit(hash_id="hash2", message="message2")
        ]
        result = self.service._parse_git_stream(stream)
        self.assertEqual(result, expected)

    @patch('subprocess.Popen')
    def test_get_commit_history_success(self, mock_popen):
        # Mock the context manager behavior of Popen
        mock_process = MagicMock()
        mock_popen.return_value.__enter__.return_value = mock_process

        # Mock stdout as an iterable of lines
        mock_process.stdout = ["h1|m1\n", "h2|m2\n"]
        # Mock returncode to be 0 (success)
        mock_process.returncode = 0
        # Mock communicate to return empty stderr
        mock_process.communicate.return_value = (None, "")

        commits = self.service.get_commit_history(2)

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].hash_id, "h1")
        self.assertEqual(commits[1].message, "m2")

        # Verify call args
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0][:5], ["git", "-C", "/tmp/repo", "log", "-n"])
        self.assertEqual(args[0][6], "--pretty=format:%h|%s")
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertEqual(kwargs['text'], True)

    @patch('subprocess.Popen')
    def test_get_commit_history_failure(self, mock_popen):
        # Mock process failure
        mock_process = MagicMock()
        mock_popen.return_value.__enter__.return_value = mock_process

        mock_process.stdout = [] # No output usually on failure
        mock_process.returncode = 1
        mock_process.communicate.return_value = (None, "git error")

        commits = self.service.get_commit_history(2)
        self.assertEqual(commits, [])

if __name__ == '__main__':
    unittest.main()
