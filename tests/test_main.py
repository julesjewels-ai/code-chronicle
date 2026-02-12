import pytest  # type: ignore
from unittest.mock import patch, MagicMock
import argparse
from typing import Generator, Dict, Any, Callable
from main import main

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def mock_dependencies() -> Generator[Dict[str, MagicMock], None, None]:
    """
    Patches all external dependencies used in main.py.
    Returns a dictionary for easy access in tests.
    """
    with patch('main.LocalGitService') as git, \
         patch('main.MockLLMService') as llm, \
         patch('main.ConsoleReportGenerator') as console_report, \
         patch('main.MarkdownReportGenerator') as md_report, \
         patch('main.ChronicleGenerator') as generator, \
         patch('main.parse_args') as parse_args, \
         patch('os.path.isdir') as isdir:

        # Default successful behavior
        mock_gen_instance = generator.return_value
        mock_gen_instance.generate.return_value = []
        isdir.return_value = True

        yield {
            'git': git,
            'llm': llm,
            'console_report': console_report,
            'md_report': md_report,
            'generator': generator,
            'parse_args': parse_args,
            'isdir': isdir
        }

# ----------------------------------------------------------------------
# Test Scenarios
# ----------------------------------------------------------------------

def setup_defaults(deps: Dict[str, MagicMock]) -> None:
    pass

def setup_invalid_path(deps: Dict[str, MagicMock]) -> None:
    deps['isdir'].return_value = False

def setup_generation_error(deps: Dict[str, MagicMock]) -> None:
    # Simulate an exception during the generation phase
    deps['generator'].return_value.generate.side_effect = Exception("Simulated Failure")

def verify_console_defaults(deps: Dict[str, MagicMock]) -> None:
    deps['git'].assert_called_once_with(".")
    deps['generator'].return_value.generate.assert_called_once_with(limit=5)
    deps['console_report'].assert_called_once()
    deps['md_report'].assert_not_called()

def verify_markdown_custom(deps: Dict[str, MagicMock]) -> None:
    deps['git'].assert_called_once_with("/custom/repo")
    deps['generator'].return_value.generate.assert_called_once_with(limit=10)
    deps['md_report'].assert_called_once()
    deps['console_report'].assert_not_called()

def verify_error_handling(deps: Dict[str, MagicMock]) -> None:
    # Ensure generator was called before failure
    deps['generator'].return_value.generate.assert_called_once()

# ----------------------------------------------------------------------
# Parametrized Test
# ----------------------------------------------------------------------

@pytest.mark.parametrize("scenario", [
    {
        "id": "defaults_console",
        "description": "Standard execution with default arguments (console)",
        "args": argparse.Namespace(path='.', limit=5, format='console'),
        "setup": setup_defaults,
        "expect_exit": False,
        "expected_stderr": None,
        "expected_stdout": "Initializing CodeChronicle",
        "verify": verify_console_defaults
    },
    {
        "id": "custom_markdown",
        "description": "Custom execution with markdown format",
        "args": argparse.Namespace(path='/custom/repo', limit=10, format='markdown'),
        "setup": setup_defaults,
        "expect_exit": False,
        "expected_stderr": None,
        "expected_stdout": None, # Markdown mode doesn't print init message in current code
        "verify": verify_markdown_custom
    },
    {
        "id": "invalid_path",
        "description": "Execution with invalid path should exit early",
        "args": argparse.Namespace(path='/invalid/path', limit=5, format='console'),
        "setup": setup_invalid_path,
        "expect_exit": True,
        "expected_stderr": "Error: The path '/invalid/path' is not a valid directory.",
        "expected_stdout": None,
        "verify": lambda d: None
    },
    {
        "id": "exception_handling",
        "description": "Exception during generation should be caught and exit",
        "args": argparse.Namespace(path='.', limit=5, format='console'),
        "setup": setup_generation_error,
        "expect_exit": True,
        "expected_stderr": "Error: Simulated Failure",
        "expected_stdout": "Initializing CodeChronicle",
        "verify": verify_error_handling
    }
], ids=lambda x: x["id"])
def test_main_scenarios(mock_dependencies: Dict[str, MagicMock], capsys: pytest.CaptureFixture, scenario: Dict[str, Any]) -> None:
    """
    Parametrized test covering all branches of main.py:
    1. Valid execution (Console)
    2. Valid execution (Markdown)
    3. Invalid Path (Early Exit)
    4. Runtime Exception (Late Exit)
    """
    deps = mock_dependencies

    # 1. Arrange
    deps['parse_args'].return_value = scenario["args"]
    scenario["setup"](deps)

    # 2. Act & Assert
    if scenario["expect_exit"]:
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
    else:
        main()

    # 3. Verify Output
    captured = capsys.readouterr()

    if scenario["expected_stderr"]:
        assert scenario["expected_stderr"] in captured.err

    if scenario["expected_stdout"]:
        assert scenario["expected_stdout"] in captured.out

    # 4. Verify side effects
    if scenario["verify"]:
        scenario["verify"](deps)
