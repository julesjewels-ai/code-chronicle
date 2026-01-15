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

    @patch('subprocess.run')
    def test_get_commit_history_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "h1|m1\nh2|m2"
        mock_run.return_value = mock_result

        commits = self.service.get_commit_history(2)

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].hash_id, "h1")
        self.assertEqual(commits[1].message, "m2")

        # Verify call args
        args, _ = mock_run.call_args
        self.assertEqual(args[0][:5], ["git", "-C", "/tmp/repo", "log", "-n"])
        self.assertEqual(args[0][6], "--pretty=format:%h|%s")

    @patch('subprocess.run')
    def test_get_commit_history_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, ['git'])

        with self.assertRaises(subprocess.CalledProcessError):
            self.service.get_commit_history(2)

if __name__ == '__main__':
    unittest.main()
