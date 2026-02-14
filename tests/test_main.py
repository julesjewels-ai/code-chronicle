import pytest  # type: ignore
from unittest.mock import patch
import argparse
import os
from main import main

@pytest.fixture
def mock_dependencies():
    with patch('main.LocalGitService') as git, \
         patch('main.MockLLMService') as mock_llm, \
         patch('main.OpenAILLMService') as openai_llm, \
         patch('main.ConsoleReportGenerator') as console_report, \
         patch('main.MarkdownReportGenerator') as md_report, \
         patch('main.ChronicleGenerator') as generator, \
         patch('main.parse_args') as parse_args, \
         patch('os.path.isdir') as isdir, \
         patch('main.load_dotenv') as load_dotenv, \
         patch.dict(os.environ, {}, clear=True):  # Clear env vars

        # Setup common behavior
        mock_gen_instance = generator.return_value
        mock_gen_instance.generate.return_value = []
        isdir.return_value = True

        yield {
            'git': git,
            'mock_llm': mock_llm,
            'openai_llm': openai_llm,
            'console_report': console_report,
            'md_report': md_report,
            'generator': generator,
            'parse_args': parse_args,
            'isdir': isdir,
            'load_dotenv': load_dotenv
        }

def test_main_defaults_mock_llm(mock_dependencies):
    deps = mock_dependencies['parse_args']
    deps.return_value = argparse.Namespace(path='.', limit=5, format='console', api_key=None, model='gpt-4o')

    main()

    mock_dependencies['git'].assert_called_once_with(".")
    mock_dependencies['generator'].return_value.generate.assert_called_once_with(limit=5)
    mock_dependencies['mock_llm'].assert_called_once()
    mock_dependencies['openai_llm'].assert_not_called()

def test_main_api_key_cli(mock_dependencies):
    deps = mock_dependencies['parse_args']
    deps.return_value = argparse.Namespace(path='.', limit=5, format='console', api_key='sk-cli', model='gpt-4o')

    main()

    mock_dependencies['openai_llm'].assert_called_once_with(api_key='sk-cli', model='gpt-4o')
    mock_dependencies['mock_llm'].assert_not_called()

def test_main_api_key_env(mock_dependencies):
    deps = mock_dependencies['parse_args']
    deps.return_value = argparse.Namespace(path='.', limit=5, format='console', api_key=None, model='gpt-4o')

    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-env"}):
        main()

    mock_dependencies['openai_llm'].assert_called_once_with(api_key='sk-env', model='gpt-4o')
    mock_dependencies['mock_llm'].assert_not_called()

def test_main_custom_args(mock_dependencies):
    deps = mock_dependencies['parse_args']
    deps.return_value = argparse.Namespace(path='/custom/repo', limit=10, format='markdown', api_key=None, model='gpt-4o')

    main()

    mock_dependencies['git'].assert_called_once_with("/custom/repo")
    mock_dependencies['generator'].return_value.generate.assert_called_once_with(limit=10)
    mock_dependencies['md_report'].assert_called_once()

def test_main_invalid_path(mock_dependencies):
    deps = mock_dependencies['parse_args']
    deps.return_value = argparse.Namespace(path='/invalid/path', limit=5, format='console', api_key=None, model='gpt-4o')
    mock_dependencies['isdir'].return_value = False

    # We verify it exits
    with pytest.raises(SystemExit):
        main()
