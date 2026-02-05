import pytest  # type: ignore
from src.cli import parse_args

def test_defaults():
    args = parse_args([])
    assert args.path == "."
    assert args.limit == 5
    assert args.format == "console"

def test_custom_args():
    args = parse_args(["/path/to/repo", "-n", "10", "-f", "markdown"])
    assert args.path == "/path/to/repo"
    assert args.limit == 10
    assert args.format == "markdown"

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
