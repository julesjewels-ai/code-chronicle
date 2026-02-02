import unittest
from unittest.mock import MagicMock
from src.core.engine import ChronicleGenerator
from src.models import Commit, AnalyzedCommit

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
        results = list(generator.generate(limit=1))

        # Assertions
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], AnalyzedCommit)
        self.assertEqual(results[0].commit.hash_id, "123")
        self.assertEqual(results[0].analysis, "analysis")

        mock_git.get_commit_history.assert_called_with(1)
        mock_llm.analyze_commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
