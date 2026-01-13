import unittest
from src.services.git import LocalGitService
from src.models import Commit

class TestLocalGitService(unittest.TestCase):
    def test_parse_git_log_normal(self):
        output = "hash1|message1\nhash2|message2"
        commits = LocalGitService._parse_git_log(output)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].hash_id, "hash1")
        self.assertEqual(commits[0].message, "message1")
        self.assertEqual(commits[1].hash_id, "hash2")
        self.assertEqual(commits[1].message, "message2")

    def test_parse_git_log_with_empty_lines(self):
        output = "\nhash1|message1\n\n"
        commits = LocalGitService._parse_git_log(output)
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].hash_id, "hash1")

    def test_parse_git_log_missing_separator(self):
        output = "hash1|message1\ninvalid_line"
        commits = LocalGitService._parse_git_log(output)
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].hash_id, "hash1")

    def test_parse_git_log_multiple_separators(self):
        # Should only split on first |
        output = "hash1|feat: add | pipe"
        commits = LocalGitService._parse_git_log(output)
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].hash_id, "hash1")
        self.assertEqual(commits[0].message, "feat: add | pipe")

    def test_parse_git_log_empty_hash(self):
        # Current implementation allows empty hash if | is present
        output = "|message"
        commits = LocalGitService._parse_git_log(output)
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].hash_id, "")
        self.assertEqual(commits[0].message, "message")

if __name__ == '__main__':
    unittest.main()
