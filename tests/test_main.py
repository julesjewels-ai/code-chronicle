import sys
import pytest
from pytest_mock import MockerFixture
from unittest.mock import MagicMock
from main import main
from src.core.engine import ChronicleGenerator
from src.services.git import LocalGitService
from src.services.llm import MockLLMService
from src.services.report import ConsoleReportGenerator, MarkdownReportGenerator
from src.models import AnalyzedCommit, Commit
import argparse

@pytest.fixture
def mock_dependencies(mocker: MockerFixture) -> dict:
    """Mocks all dependencies used in main.py."""
    # Create mocks
    mock_parse_args = mocker.patch('main.parse_args')
    mock_isdir = mocker.patch('os.path.isdir')
    mock_git_service_cls = mocker.patch('main.LocalGitService')
    mock_llm_service_cls = mocker.patch('main.MockLLMService')
    mock_console_report_cls = mocker.patch('main.ConsoleReportGenerator')
    mock_markdown_report_cls = mocker.patch('main.MarkdownReportGenerator')
    mock_chronicle_generator_cls = mocker.patch('main.ChronicleGenerator')
    mock_sys_exit = mocker.patch('sys.exit')

    # Configure defaults
    mock_isdir.return_value = True

    # Configure Generator instance
    mock_generator_instance = mock_chronicle_generator_cls.return_value
    mock_generator_instance.generate.return_value = [
        AnalyzedCommit(
            commit=Commit(hash_id="123", message="test commit"),
            analysis="analysis"
        )
    ]

    # Configure Report Generator instances
    mock_console_report_instance = mock_console_report_cls.return_value
    mock_console_report_instance.generate.return_value = "Console Report Story"

    mock_markdown_report_instance = mock_markdown_report_cls.return_value
    mock_markdown_report_instance.generate.return_value = "Markdown Report Story"

    return {
        'parse_args': mock_parse_args,
        'isdir': mock_isdir,
        'git_service_cls': mock_git_service_cls,
        'llm_service_cls': mock_llm_service_cls,
        'console_report_cls': mock_console_report_cls,
        'markdown_report_cls': mock_markdown_report_cls,
        'chronicle_generator_cls': mock_chronicle_generator_cls,
        'sys_exit': mock_sys_exit,
        'generator_instance': mock_generator_instance
    }

@pytest.mark.parametrize("scenario", [
    {
        "description": "Standard execution with console format",
        "args": argparse.Namespace(path='.', limit=5, format='console'),
        "is_dir": True,
        "exception_trigger": None,
        "expected_exit_code": None,
        "expected_stdout_contains": ["Initializing CodeChronicle for: .", "Console Report Story"],
        "expected_stderr_contains": [],
        "expected_report_class": "ConsoleReportGenerator"
    },
    {
        "description": "Standard execution with markdown format",
        "args": argparse.Namespace(path='/repo', limit=10, format='markdown'),
        "is_dir": True,
        "exception_trigger": None,
        "expected_exit_code": None,
        "expected_stdout_contains": ["Markdown Report Story"],
        "expected_stderr_contains": [], # Markdown format doesn't print "Initializing..."
        "expected_report_class": "MarkdownReportGenerator"
    },
    {
        "description": "Invalid directory path",
        "args": argparse.Namespace(path='/invalid', limit=5, format='console'),
        "is_dir": False,
        "exception_trigger": None,
        "expected_exit_code": 1,
        "expected_stdout_contains": [],
        "expected_stderr_contains": ["Error: The path '/invalid' is not a valid directory."],
        "expected_report_class": None
    },
    {
        "description": "Exception during execution (e.g. generation fails)",
        "args": argparse.Namespace(path='.', limit=5, format='console'),
        "is_dir": True,
        "exception_trigger": ValueError("Generation failed"),
        "expected_exit_code": 1,
        "expected_stdout_contains": ["Initializing CodeChronicle for: ."],
        "expected_stderr_contains": ["Error: Generation failed"],
        "expected_report_class": "ConsoleReportGenerator"
    }
])
def test_main_scenarios(mock_dependencies: dict, capsys: pytest.CaptureFixture, scenario: dict) -> None:
    # Arrange
    mock_dependencies['parse_args'].return_value = scenario['args']
    mock_dependencies['isdir'].return_value = scenario['is_dir']

    if scenario['exception_trigger']:
        mock_dependencies['generator_instance'].generate.side_effect = scenario['exception_trigger']

    # Mock sys.exit to raise SystemExit so we can catch it and verify flow interruption
    mock_dependencies['sys_exit'].side_effect = SystemExit(scenario['expected_exit_code'])

    # Act
    try:
        main()
    except SystemExit:
        pass

    # Assert
    # Check exit code
    if scenario['expected_exit_code'] is not None:
        mock_dependencies['sys_exit'].assert_called_with(scenario['expected_exit_code'])
    else:
        mock_dependencies['sys_exit'].assert_not_called()

    # Check Output
    captured = capsys.readouterr()

    for msg in scenario['expected_stdout_contains']:
        assert msg in captured.out, f"Expected '{msg}' in stdout for {scenario['description']}"

    for msg in scenario['expected_stderr_contains']:
        assert msg in captured.err, f"Expected '{msg}' in stderr for {scenario['description']}"

    # Verify Report Generator Selection (only if successful path)
    if scenario['expected_exit_code'] is None:
        if scenario['expected_report_class'] == "ConsoleReportGenerator":
            mock_dependencies['console_report_cls'].assert_called_once()
            mock_dependencies['markdown_report_cls'].assert_not_called()
        elif scenario['expected_report_class'] == "MarkdownReportGenerator":
            mock_dependencies['markdown_report_cls'].assert_called_once()
            mock_dependencies['console_report_cls'].assert_not_called()

    # Verify Generator call arguments (only if successful path)
    if scenario['expected_exit_code'] is None:
        mock_dependencies['generator_instance'].generate.assert_called_with(limit=scenario['args'].limit)
