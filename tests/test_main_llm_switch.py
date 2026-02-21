import argparse
from main import main

def test_main_uses_openai_service_if_key_present(mocker):
    # Setup dependencies
    mocker.patch('main.load_dotenv')
    mocker.patch('main.LocalGitService')
    mocker.patch('main.ConsoleReportGenerator')
    mocker.patch('main.MarkdownReportGenerator')
    mocker.patch('main.ChronicleGenerator')
    mocker.patch('os.path.isdir', return_value=True)
    mocker.patch('main.parse_args', return_value=argparse.Namespace(path='.', limit=5, format='console'))

    # Set env var
    mocker.patch('os.getenv', side_effect=lambda key: "test_key" if key == "OPENAI_API_KEY" else None)

    mock_openai = mocker.patch('main.OpenAILLMService')
    mock_mock_llm = mocker.patch('main.MockLLMService')

    main()

    mock_openai.assert_called_once_with("test_key")
    mock_mock_llm.assert_not_called()

def test_main_uses_mock_llm_if_key_missing(mocker):
    # Setup dependencies
    mocker.patch('main.load_dotenv')
    mocker.patch('main.LocalGitService')
    mocker.patch('main.ConsoleReportGenerator')
    mocker.patch('main.MarkdownReportGenerator')
    mocker.patch('main.ChronicleGenerator')
    mocker.patch('os.path.isdir', return_value=True)
    mocker.patch('main.parse_args', return_value=argparse.Namespace(path='.', limit=5, format='console'))

    # Set env var to None
    mocker.patch('os.getenv', side_effect=lambda key: None if key == "OPENAI_API_KEY" else None)

    mock_openai = mocker.patch('main.OpenAILLMService')
    mock_mock_llm = mocker.patch('main.MockLLMService')

    main()

    mock_openai.assert_not_called()
    mock_mock_llm.assert_called_once()
