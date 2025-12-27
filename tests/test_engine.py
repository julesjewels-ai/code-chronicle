import unittest
from unittest.mock import MagicMock
from src.core.engine import ChronicleGenerator
from src.models import Commit

class TestChronicleGenerator(unittest.TestCase):
    def test_generate(self):
        # Mock dependencies
        mock_git = MagicMock()
        mock_llm = MagicMock()

        # Setup mock return values
        mock_git.get_commit_history.return_value = [
            Commit(hash_id="123", message="test commit")
        ]
        mock_llm.analyze_commit.return_value = "analysis"

        # Instantiate generator
        generator = ChronicleGenerator(mock_git, mock_llm)

        # Run generation
        result = generator.generate(limit=1)

        # Assertions
        self.assertIn("Commit 123: test commit", result)
        self.assertIn("-> analysis", result)
        mock_git.get_commit_history.assert_called_with(1)
        mock_llm.analyze_commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
