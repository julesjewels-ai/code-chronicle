import unittest
from unittest.mock import MagicMock, patch
from src.services.git import LocalGitService
from src.models import Commit

class TestLocalGitService(unittest.TestCase):
    def setUp(self):
        self.service = LocalGitService("/tmp/repo")

    def test_parse_git_log_valid(self):
        output = "a1b2c3d|Initial commit\ne5f6g7h|Fix bug"
        commits = self.service._parse_git_log(output)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].hash_id, "a1b2c3d")
        self.assertEqual(commits[0].message, "Initial commit")
        self.assertEqual(commits[1].hash_id, "e5f6g7h")
        self.assertEqual(commits[1].message, "Fix bug")

    def test_parse_git_log_empty(self):
        output = ""
        commits = self.service._parse_git_log(output)
        self.assertEqual(len(commits), 0)

    def test_parse_git_log_malformed(self):
        output = "valid|commit\ninvalid_line\nanother|valid"
        commits = self.service._parse_git_log(output)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].hash_id, "valid")
        self.assertEqual(commits[1].hash_id, "another")

    def test_parse_git_log_extra_separators(self):
        output = "hash|message with | pipe"
        commits = self.service._parse_git_log(output)
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].hash_id, "hash")
        self.assertEqual(commits[0].message, "message with | pipe")
