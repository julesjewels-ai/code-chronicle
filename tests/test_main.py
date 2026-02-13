import pytest  # type: ignore
from unittest.mock import patch, MagicMock
import argparse
from typing import Generator, Any, Dict
from main import main

@pytest.fixture
def mock_dependencies() -> Generator[Dict[str, MagicMock], None, None]:
    """Mock external dependencies for main.py."""
    with patch('main.LocalGitService') as git, \
         patch('main.MockLLMService') as llm, \
         patch('main.ConsoleReportGenerator') as console_report, \
         patch('main.MarkdownReportGenerator') as md_report, \
         patch('main.ChronicleGenerator') as generator, \
         patch('main.parse_args') as parse_args, \
         patch('os.path.isdir') as isdir:

        # Setup common behavior
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

@pytest.mark.parametrize("scenario, args, expected_calls, expected_output, expected_exit", [
    (
        "defaults",
        argparse.Namespace(path='.', limit=5, format='console'),
        {
            'git_args': ('.',),
            'gen_limit': 5,
            'report_cls': 'console_report'
        },
        "Initializing CodeChronicle for: .",
        None
    ),
    (
        "custom_args",
        argparse.Namespace(path='/custom/repo', limit=10, format='markdown'),
        {
            'git_args': ('/custom/repo',),
            'gen_limit': 10,
            'report_cls': 'md_report'
        },
        None,  # No output for markdown format unless error
        None
    ),
    (
        "invalid_path",
        argparse.Namespace(path='/invalid/path', limit=5, format='console'),
        {},
        "Error: The path '/invalid/path' is not a valid directory.",
        1
    ),
    (
        "execution_error",
        argparse.Namespace(path='.', limit=5, format='console'),
        {
            'git_args': ('.',),
            'gen_limit': 5,
            'report_cls': 'console_report',
            'raise_error': Exception("Simulated Failure")
        },
        "Error: Simulated Failure",
        1
    ),
])
def test_main_scenarios(
    mock_dependencies: Dict[str, MagicMock],
    capsys: pytest.CaptureFixture[str],
    scenario: str,
    args: argparse.Namespace,
    expected_calls: Dict[str, Any],
    expected_output: str | None,
    expected_exit: int | None
) -> None:
    """Test main function with various scenarios."""
    deps = mock_dependencies
    deps['parse_args'].return_value = args

    # Handle specific setup for invalid path
    if scenario == "invalid_path":
        deps['isdir'].return_value = False

    # Handle specific setup for execution error
    if 'raise_error' in expected_calls:
        deps['generator'].return_value.generate.side_effect = expected_calls['raise_error']

    # Execute main
    if expected_exit is not None:
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == expected_exit
    else:
        main()

    # Verify Output
    captured = capsys.readouterr()
    if expected_output:
        # Check if output is in stdout or stderr
        assert expected_output in captured.out or expected_output in captured.err

    # Verify Calls if applicable
    if expected_calls:
        if 'git_args' in expected_calls:
            deps['git'].assert_called_once_with(*expected_calls['git_args'])

        if 'gen_limit' in expected_calls:
            deps['generator'].return_value.generate.assert_called_once_with(limit=expected_calls['gen_limit'])

        if 'report_cls' in expected_calls:
            report_cls_key = expected_calls['report_cls']
            deps[report_cls_key].assert_called_once()

            # Ensure the other report generator wasn't called
            other_cls_key = 'md_report' if report_cls_key == 'console_report' else 'console_report'
            deps[other_cls_key].assert_not_called()
