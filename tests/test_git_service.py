import unittest
from unittest.mock import MagicMock, patch
from src.services.git import LocalGitService, _parse_commit_from_line
from src.models import Commit
import subprocess

class TestLocalGitService(unittest.TestCase):
    def setUp(self):
        self.service = LocalGitService("/tmp/repo")

    def test_parse_commit_from_line_valid(self):
        line = "hash1|message1"
        expected = Commit(hash_id="hash1", message="message1")
        result = _parse_commit_from_line(line)
        self.assertEqual(result, expected)

    def test_parse_commit_from_line_empty(self):
        line = ""
        result = _parse_commit_from_line(line)
        self.assertIsNone(result)

    def test_parse_commit_from_line_malformed(self):
        line = "malformed_line_no_pipe"
        result = _parse_commit_from_line(line)
        self.assertIsNone(result)

    def test_parse_commit_from_line_extra_separator(self):
        line = "hash1|message|with|pipes"
        expected = Commit(hash_id="hash1", message="message|with|pipes")
        result = _parse_commit_from_line(line)
        self.assertEqual(result, expected)

    @patch('subprocess.Popen')
    def test_get_commit_history_success(self, mock_popen):
        process_mock = MagicMock()
        # process.stdout needs to be iterable. Since we iterate over it in the loop.
        process_mock.stdout = iter(["h1|m1\n", "h2|m2\n"])
        process_mock.wait.return_value = 0
        process_mock.__enter__.return_value = process_mock

        mock_popen.return_value = process_mock

        # Consume the iterator
        commits = list(self.service.get_commit_history(2))

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].hash_id, "h1")
        self.assertEqual(commits[1].message, "m2")

        # Verify call args
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0][:5], ["git", "-C", "/tmp/repo", "log", "-n"])
        self.assertEqual(args[0][6], "--pretty=format:%h|%s")
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['text'], True)
        # bufsize is default (-1), so it might not be in kwargs or be -1 depending on impl.
        # We removed explicitly setting it to 1.

    @patch('subprocess.Popen')
    def test_get_commit_history_failure(self, mock_popen):
        process_mock = MagicMock()
        process_mock.stdout = iter([])
        process_mock.wait.return_value = 1
        process_mock.returncode = 1
        process_mock.__enter__.return_value = process_mock

        mock_popen.return_value = process_mock

        with self.assertRaises(subprocess.CalledProcessError):
            list(self.service.get_commit_history(2))

if __name__ == '__main__':
    unittest.main()
