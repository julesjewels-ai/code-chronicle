import pytest  # type: ignore
from unittest.mock import patch
import argparse
import os
from main import main

@pytest.fixture
def mock_dependencies():
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

def test_main_defaults(mock_dependencies):
    deps = mock_dependencies
    # Provide all expected args
    deps['parse_args'].return_value = argparse.Namespace(
        path='.', limit=5, format='console', api_key=None, model='gpt-4o'
    )

    # Clear env var to ensure MockLLMService is used
    with patch.dict(os.environ, {}, clear=True):
        main()

    deps['git'].assert_called_once_with(".")
    deps['llm'].assert_called_once() # Should use MockLLMService
    deps['generator'].return_value.generate.assert_called_once_with(limit=5)
    deps['console_report'].assert_called_once()
    deps['md_report'].assert_not_called()

def test_main_custom_args(mock_dependencies):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(
        path='/custom/repo', limit=10, format='markdown', api_key=None, model='gpt-4o'
    )

    with patch.dict(os.environ, {}, clear=True):
        main()

    deps['git'].assert_called_once_with("/custom/repo")
    deps['generator'].return_value.generate.assert_called_once_with(limit=10)
    deps['md_report'].assert_called_once()
    deps['console_report'].assert_not_called()

def test_main_openai_service_arg(mock_dependencies):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(
        path='.', limit=5, format='console', api_key="sk-test", model="gpt-4o"
    )

    # Patch OpenAILLMService where it is imported
    # Since it is imported inside main inside an if block, we patch the source module
    with patch('src.services.llm.OpenAILLMService') as mock_openai_service:
        main()
        mock_openai_service.assert_called_once_with(api_key="sk-test", model="gpt-4o")
        deps['llm'].assert_not_called()

def test_main_openai_service_env(mock_dependencies):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(
        path='.', limit=5, format='console', api_key=None, model="gpt-3.5-turbo"
    )

    with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
        with patch('src.services.llm.OpenAILLMService') as mock_openai_service:
            main()
            mock_openai_service.assert_called_once_with(api_key="env-key", model="gpt-3.5-turbo")
            deps['llm'].assert_not_called()

def test_main_invalid_path(mock_dependencies):
    deps = mock_dependencies
    deps['parse_args'].return_value = argparse.Namespace(
        path='/invalid/path', limit=5, format='console', api_key=None, model='gpt-4o'
    )
    deps['isdir'].return_value = False

    # We verify it exits
    with pytest.raises(SystemExit):
        main()
