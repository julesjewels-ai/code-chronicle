import os
import sys
from dotenv import load_dotenv
from src.cli import parse_args
from src.services.git import LocalGitService
from src.services.llm import MockLLMService, OpenAILLMService
from src.services.report import ConsoleReportGenerator, MarkdownReportGenerator
from src.core.engine import ChronicleGenerator
from src.interfaces import LLMProvider

# Load environment variables from .env file
load_dotenv()

def main() -> None:
    args = parse_args()
    repo_path = args.path

    if not os.path.isdir(repo_path):
        print(f"Error: The path '{repo_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    if args.format == "console":
        print(f"Initializing CodeChronicle for: {repo_path}")

    # Initialize services
    git_service = LocalGitService(repo_path)

    llm_service: LLMProvider
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")

    if api_key:
        if args.format == "console":
            print(f"Using OpenAI Model: {args.model}")
        llm_service = OpenAILLMService(api_key=api_key, model=args.model)
    else:
        if args.format == "console":
            print("No API Key found. Using Mock LLM Service.")
        llm_service = MockLLMService()

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
