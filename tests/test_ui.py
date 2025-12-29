import unittest
from unittest.mock import MagicMock
from src.ui import print_commit, Colors
import io
import sys

class TestUI(unittest.TestCase):
    def test_print_commit_formatting(self):
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        event = {
            "hash": "abc1234",
            "message": "feat: Test commit",
            "insight": "This is a test insight"
        }

        print_commit(event)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Check for presence of ANSI codes and content
        self.assertIn("abc1234", output)
        self.assertIn("feat: Test commit", output)
        self.assertIn("This is a test insight", output)
        self.assertIn(Colors.YELLOW, output)
        self.assertIn(Colors.CYAN, output)

if __name__ == '__main__':
    unittest.main()
