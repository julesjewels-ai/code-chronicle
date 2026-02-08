import unittest
from unittest.mock import MagicMock, patch
from src.services.git import LocalGitService
import subprocess

class TestLocalGitService(unittest.TestCase):
    def setUp(self):
        self.service = LocalGitService("/tmp/repo")

    @patch('subprocess.check_output')
    @patch('subprocess.Popen')
    def test_get_commit_history_success(self, mock_popen, mock_check_output):
        process_mock = MagicMock()
        # process.stdout needs to be iterable. Since we iterate over it in the loop.
        process_mock.stdout = iter(["h1|m1\n", "h2|m2\n"])
        process_mock.wait.return_value = 0
        process_mock.__enter__.return_value = process_mock

        mock_popen.return_value = process_mock

        # Mock diff output based on hash
        def side_effect(cmd, **kwargs):
            if cmd[-1] == "h1":
                return "diff1"
            elif cmd[-1] == "h2":
                return "diff2"
            return ""

        mock_check_output.side_effect = side_effect

        # Consume the iterator
        commits = list(self.service.get_commit_history(2))

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].hash_id, "h1")
        self.assertEqual(commits[0].message, "m1")
        self.assertEqual(commits[0].diff, "diff1")

        self.assertEqual(commits[1].hash_id, "h2")
        self.assertEqual(commits[1].message, "m2")
        self.assertEqual(commits[1].diff, "diff2")

        # Verify Popen call args
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0][:5], ["git", "-C", "/tmp/repo", "log", "-n"])
        self.assertEqual(args[0][6], "--pretty=tformat:%h|%s")
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['text'], True)

        # Verify check_output calls
        self.assertEqual(mock_check_output.call_count, 2)
        # Check first call
        call_args = mock_check_output.call_args_list[0]
        self.assertEqual(call_args[0][0], ["git", "-C", "/tmp/repo", "show", "--pretty=format:", "--patch", "h1"])

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
