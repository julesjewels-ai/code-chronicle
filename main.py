import argparse
import os
import sys
from src.services.git import LocalGitService
from src.services.llm import MockLLMService
from src.services.report import ConsoleReportGenerator, MarkdownReportGenerator
from src.core.engine import ChronicleGenerator
from src.interfaces import ReportGenerator

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CodeChronicle: Turn your git log into a story.")
    parser.add_argument("path", nargs="?", default=".", help="Path to the git repository")
    parser.add_argument("-n", "--limit", type=int, default=5, help="Number of commits to analyze")
    parser.add_argument("-f", "--format", choices=["console", "markdown"], default="console", help="Output format")
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    
    repo_path = args.path
    if not os.path.isdir(repo_path):
        print(f"Error: Path '{repo_path}' is not a directory.")
        sys.exit(1)

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
        # Generate a story from the last limit commits
        analyzed_commits = generator.generate(limit=args.limit)
        story = report_service.generate(analyzed_commits)
        print("\n=== Code Evolution Narrative ===\n")
        print(story)
        print("\n=== End of Story ===")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
