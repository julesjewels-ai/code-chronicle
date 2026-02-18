import argparse

def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CodeChronicle: Turn git history into a narrative.")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the repository (default: current directory)"
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=5,
        help="Number of commits to analyze (default: 5)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["console", "markdown"],
        default="console",
        help="Output format (default: console)"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API Key (optional, can be set via OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.limit < 1:
        parser.error("Limit must be a positive integer.")

    return parsed_args
