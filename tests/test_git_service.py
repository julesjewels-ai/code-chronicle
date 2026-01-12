import unittest
from src.services.git import LocalGitService
from src.models import Commit

class TestLocalGitService(unittest.TestCase):
    def test_parse_git_log(self):
        service = LocalGitService(".")

        # Test case 1: Standard output
        output = "abc1234|Initial commit\ndef5678|Fix bug"
        expected = [
            Commit(hash_id="abc1234", message="Initial commit"),
            Commit(hash_id="def5678", message="Fix bug")
        ]
        self.assertEqual(service._parse_git_log(output), expected)

    def test_parse_git_log_empty(self):
        service = LocalGitService(".")
        self.assertEqual(service._parse_git_log(""), [])
        self.assertEqual(service._parse_git_log("\n"), [])

    def test_parse_git_log_malformed(self):
        service = LocalGitService(".")
        # Should skip malformed lines
        output = "valid|line\nmalformed_line\nanother|valid"
        expected = [
            Commit(hash_id="valid", message="line"),
            Commit(hash_id="another", message="valid")
        ]
        self.assertEqual(service._parse_git_log(output), expected)

if __name__ == '__main__':
    unittest.main()
