import pytest
import argparse
from main import main

@pytest.fixture
def mock_dependencies(mocker):
    # Using mocker fixture for cleaner patches
    git = mocker.patch('main.LocalGitService')
    mock_llm = mocker.patch('main.MockLLMService')
    openai_llm = mocker.patch('main.OpenAILLMService')
    console_report = mocker.patch('main.ConsoleReportGenerator')
    md_report = mocker.patch('main.MarkdownReportGenerator')
    generator = mocker.patch('main.ChronicleGenerator')
    parse_args = mocker.patch('main.parse_args')
    isdir = mocker.patch('os.path.isdir')
    mocker.patch('main.load_dotenv')
    getenv = mocker.patch('os.getenv')

    # Setup common behavior
    mock_gen_instance = generator.return_value
    mock_gen_instance.generate.return_value = []
    isdir.return_value = True
    getenv.return_value = None  # Default to no API key

    return {
        'git': git,
        'mock_llm': mock_llm,
        'openai_llm': openai_llm,
        'console_report': console_report,
        'md_report': md_report,
        'generator': generator,
        'parse_args': parse_args,
        'isdir': isdir,
        'getenv': getenv
    }

def test_main_defaults_no_api_key(mock_dependencies):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(path='.', limit=5, format='console')
    deps['getenv'].return_value = None

    main()

    deps['git'].assert_called_once_with(".")
    deps['mock_llm'].assert_called_once()
    deps['openai_llm'].assert_not_called()
    deps['generator'].assert_called_once() # Verify generator init
    # Check generator called with correct LLM service
    args, _ = deps['generator'].call_args
    assert args[1] == deps['mock_llm'].return_value

def test_main_with_api_key(mock_dependencies):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(path='.', limit=5, format='console')
    deps['getenv'].return_value = "sk-test-key"

    main()

    deps['git'].assert_called_once_with(".")
    deps['openai_llm'].assert_called_once_with(api_key="sk-test-key")
    deps['mock_llm'].assert_not_called()

    # Check generator called with correct LLM service
    args, _ = deps['generator'].call_args
    assert args[1] == deps['openai_llm'].return_value

def test_main_custom_args(mock_dependencies):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(path='/custom/repo', limit=10, format='markdown')

    main()

    deps['git'].assert_called_once_with("/custom/repo")
    deps['generator'].return_value.generate.assert_called_once_with(limit=10)
    deps['md_report'].assert_called_once()

def test_main_invalid_path(mock_dependencies):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(path='/invalid/path', limit=5, format='console')
    deps['isdir'].return_value = False

    with pytest.raises(SystemExit):
        main()
