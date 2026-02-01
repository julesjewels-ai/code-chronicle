import unittest
from unittest.mock import MagicMock, patch
from src.services.git import LocalGitService
from src.models import Commit
import subprocess

class TestLocalGitService(unittest.TestCase):
    def setUp(self):
        self.service = LocalGitService("/tmp/repo")

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
        self.assertEqual(args[0][6], "--pretty=tformat:%h|%s")
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['text'], True)

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
