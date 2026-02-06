import os
import sys
from src.cli import parse_args
from src.interfaces import LLMProvider
from src.services.git import LocalGitService
from src.services.llm import MockLLMService, OpenAILLMService
from src.services.report import ConsoleReportGenerator, MarkdownReportGenerator
from src.core.engine import ChronicleGenerator

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

    llm_service: LLMProvider
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm_service = OpenAILLMService(api_key=api_key)
        if args.format == "console":
            print("Using OpenAI LLM Service")
    else:
        llm_service = MockLLMService()
        if args.format == "console":
            print("Using Mock LLM Service (set OPENAI_API_KEY to use real LLM)", file=sys.stderr)

    report_generators = {
        "console": ConsoleReportGenerator,
        "markdown": MarkdownReportGenerator,
    }
    report_service = report_generators[args.format]()

    # Initialize Engine with dependencies
    generator = ChronicleGenerator(git_service, llm_service)

    try:
        # Generate a story from the last N commits
        analyzed_commits = generator.generate(limit=args.limit)
        story = report_service.generate(analyzed_commits)
        print(story)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
