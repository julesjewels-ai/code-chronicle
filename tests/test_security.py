import unittest
import os
from src.core.app import CodeChronicleApp

class TestAppSecurity(unittest.TestCase):
    def test_invalid_repo_path(self):
        """Test that initializing with a non-existent path raises an error."""
        with self.assertRaises(ValueError) as cm:
            CodeChronicleApp("/non/existent/path")
        self.assertIn("Repository path does not exist", str(cm.exception))

    def test_command_injection_attempt_limit(self):
        """Test that passing malicious strings to limit raises ValueError."""
        app = CodeChronicleApp(".")
        malicious_input = "5; echo 'hacked'"

        with self.assertRaises(ValueError) as cm:
            app.generate_narrative(limit=malicious_input)
        self.assertIn("Limit must be a positive integer", str(cm.exception))

    def test_negative_limit(self):
        """Test that negative limit raises ValueError."""
        app = CodeChronicleApp(".")
        with self.assertRaises(ValueError) as cm:
            app.generate_narrative(limit=-1)
        self.assertIn("Limit must be a positive integer", str(cm.exception))

    def test_valid_usage(self):
        """Test valid usage works."""
        app = CodeChronicleApp(".")
        # Should not raise
        app.generate_narrative(limit=1)

if __name__ == '__main__':
    unittest.main()
