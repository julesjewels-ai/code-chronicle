import argparse
import os
import sys
from src.services.git import LocalGitService
from src.services.llm import MockLLMService
from src.services.report import ConsoleReportGenerator, MarkdownReportGenerator, ReportGenerator
from src.core.engine import ChronicleGenerator

def parse_args() -> argparse.Namespace:
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
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    repo_path = args.path

    if not os.path.isdir(repo_path):
        print(f"Error: The path '{repo_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # Only print initialization message to stderr to avoid polluting stdout if piping
    # or just keep it simple. The original code printed to stdout.
    # Given the 'console' vs 'markdown' distinction, it's better to keep logging separate from output.
    # But for 'console' format, it's fine.
    # I'll print to stderr for info messages if format is markdown?
    # Let's stick to the previous behavior but maybe cleaner.
    if args.format == "console":
        print(f"Initializing CodeChronicle for: {repo_path}")

    # Initialize services
    git_service = LocalGitService(repo_path)
    llm_service = MockLLMService()

    report_service: ReportGenerator
    if args.format == "markdown":
        report_service = MarkdownReportGenerator()
    else:
        report_service = ConsoleReportGenerator()

    # Initialize Engine with dependencies
    generator = ChronicleGenerator(git_service, llm_service)

    try:
        # Generate a story from the last N commits
        analyzed_commits = generator.generate(limit=args.limit)
        story = report_service.generate(analyzed_commits)

        if args.format == "console":
            print("\n=== Code Evolution Narrative ===\n")
            print(story)
            print("\n=== End of Story ===")
        else:
            print(story)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
