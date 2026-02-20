import pytest
from unittest.mock import patch, MagicMock
from main import main

@pytest.fixture
def mock_dependencies():
    with patch('main.LocalGitService') as git, \
         patch('main.MockLLMService') as mock_llm, \
         patch('main.OpenAILLMService') as openai_llm, \
         patch('main.ConsoleReportGenerator'), \
         patch('main.ChronicleGenerator') as generator, \
         patch('main.parse_args') as parse_args, \
         patch('os.path.isdir') as isdir, \
         patch('dotenv.load_dotenv'):

        isdir.return_value = True
        yield {
            'git': git,
            'mock_llm': mock_llm,
            'openai_llm': openai_llm,
            'generator': generator,
            'parse_args': parse_args
        }

def test_main_uses_mock_llm_by_default(mock_dependencies, mocker):
    deps = mock_dependencies
    # Ensure OPENAI_API_KEY is not present
    mocker.patch.dict("os.environ", {}, clear=True)
    deps['parse_args'].return_value = MagicMock(path='.', limit=5, format='console')

    main()

    deps['mock_llm'].assert_called_once()
    deps['openai_llm'].assert_not_called()

def test_main_uses_openai_llm_when_key_present(mock_dependencies, mocker):
    deps = mock_dependencies
    mocker.patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"})
    deps['parse_args'].return_value = MagicMock(path='.', limit=5, format='console')

    main()

    deps['openai_llm'].assert_called_once()
    deps['mock_llm'].assert_not_called()
