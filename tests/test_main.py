import pytest  # type: ignore
import argparse
from main import main

@pytest.fixture
def mock_dependencies(mocker):
    git = mocker.patch('main.LocalGitService')
    llm = mocker.patch('main.MockLLMService')
    console_report = mocker.patch('main.ConsoleReportGenerator')
    md_report = mocker.patch('main.MarkdownReportGenerator')
    generator = mocker.patch('main.ChronicleGenerator')
    parse_args = mocker.patch('main.parse_args')
    isdir = mocker.patch('os.path.isdir')

    # Setup common behavior
    mock_gen_instance = generator.return_value
    mock_gen_instance.generate.return_value = []
    isdir.return_value = True

    return {
        'git': git,
        'llm': llm,
        'console_report': console_report,
        'md_report': md_report,
        'generator': generator,
        'parse_args': parse_args,
        'isdir': isdir
    }

def test_main_defaults(mock_dependencies):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(path='.', limit=5, format='console')

    main()

    deps['git'].assert_called_once_with(".")
    deps['generator'].return_value.generate.assert_called_once_with(limit=5)
    deps['console_report'].assert_called_once()
    deps['md_report'].assert_not_called()

def test_main_custom_args(mock_dependencies):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(path='/custom/repo', limit=10, format='markdown')

    main()

    deps['git'].assert_called_once_with("/custom/repo")
    deps['generator'].return_value.generate.assert_called_once_with(limit=10)
    deps['md_report'].assert_called_once()
    deps['console_report'].assert_not_called()

def test_main_invalid_path(mock_dependencies, capsys):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(path='/invalid/path', limit=5, format='console')
    deps['isdir'].return_value = False

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "Error: The path '/invalid/path' is not a valid directory." in captured.err

@pytest.mark.parametrize("exception_cls, expected_msg", [
    (Exception, "Generic Error"),
    (ValueError, "Value Error"),
])
def test_main_exception(mock_dependencies, capsys, exception_cls, expected_msg):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(path='.', limit=5, format='console')

    # Mock generator to raise Exception
    deps['generator'].return_value.generate.side_effect = exception_cls(expected_msg)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert f"Error: {expected_msg}" in captured.err
