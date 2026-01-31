import unittest
from unittest.mock import MagicMock, patch
from src.services.git import LocalGitService
import subprocess

class TestLocalGitService(unittest.TestCase):
    def setUp(self):
        self.service = LocalGitService("/tmp/repo")

    @patch('subprocess.Popen')
    def test_get_commit_history_success(self, mock_popen):
        process_mock = MagicMock()

        # Simulate stream output with record separators
        # format: hash|author|date|subject|body(multiline)RecordSep
        # Using \x1f as field sep, \x1e as record sep

        chunk1 = "h1\x1fAlice\x1f2024-01-01\x1fSubject 1\x1fBody 1 line 1\nBody 1 line 2\x1e"
        chunk2 = "h2\x1fBob\x1f2024-01-02\x1fSubject 2\x1fBody 2\x1e"

        # Mocking read to return the full content then empty string
        process_mock.stdout.read.side_effect = [chunk1 + chunk2, ""]
        process_mock.wait.return_value = 0
        process_mock.__enter__.return_value = process_mock

        mock_popen.return_value = process_mock

        # Consume the iterator
        commits = list(self.service.get_commit_history(2))

        self.assertEqual(len(commits), 2)

        self.assertEqual(commits[0].hash_id, "h1")
        self.assertEqual(commits[0].author, "Alice")
        self.assertEqual(commits[0].date, "2024-01-01")
        self.assertEqual(commits[0].message, "Subject 1")
        self.assertEqual(commits[0].body, "Body 1 line 1\nBody 1 line 2")

        self.assertEqual(commits[1].hash_id, "h2")
        self.assertEqual(commits[1].author, "Bob")
        self.assertEqual(commits[1].body, "Body 2")

        # Verify call args
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0][:5], ["git", "-C", "/tmp/repo", "log", "-n"])
        # Verify the format string contains our separators
        cmd_str = args[0][6]
        self.assertIn("%x1f", cmd_str)
        self.assertIn("%x1e", cmd_str)
        self.assertIn("%an", cmd_str) # author name
        self.assertIn("%ad", cmd_str) # author date
        self.assertIn("%b", cmd_str)  # body

    @patch('subprocess.Popen')
    def test_get_commit_history_failure(self, mock_popen):
        process_mock = MagicMock()
        process_mock.stdout.read.return_value = ""
        process_mock.wait.return_value = 1
        process_mock.returncode = 1
        process_mock.__enter__.return_value = process_mock

        mock_popen.return_value = process_mock

        with self.assertRaises(subprocess.CalledProcessError):
            list(self.service.get_commit_history(2))

if __name__ == '__main__':
    unittest.main()
