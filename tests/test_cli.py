import pytest  # type: ignore
from src.cli import parse_args

def test_defaults():
    args = parse_args([])
    assert args.path == "."
    assert args.limit == 5
    assert args.format == "console"
    assert args.api_key is None
    assert args.model == "gpt-4o"

def test_custom_args():
    args = parse_args(["/path/to/repo", "-n", "10", "-f", "markdown", "--api-key", "sk-test", "--model", "gpt-3.5-turbo"])
    assert args.path == "/path/to/repo"
    assert args.limit == 10
    assert args.format == "markdown"
    assert args.api_key == "sk-test"
    assert args.model == "gpt-3.5-turbo"

def test_long_args():
    args = parse_args(["--limit", "20", "--format", "console"])
    assert args.limit == 20
    assert args.format == "console"

def test_invalid_limit():
    # argparse calls sys.exit(2) on error
    with pytest.raises(SystemExit):
        parse_args(["-n", "0"])

    with pytest.raises(SystemExit):
        parse_args(["-n", "-1"])

def test_invalid_format():
    with pytest.raises(SystemExit):
        parse_args(["-f", "xml"])
