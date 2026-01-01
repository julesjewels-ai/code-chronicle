import sys
from src.services.git import LocalGitService
from src.services.llm import MockLLMService
from src.core.engine import ChronicleGenerator

def main() -> None:
    # Use current directory by default if no path provided
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"Initializing CodeChronicle for: {repo_path}")

    # Initialize services
    git_service = LocalGitService(repo_path)
    llm_service = MockLLMService()

    # Initialize Engine with dependencies
    generator = ChronicleGenerator(git_service, llm_service)

    try:
        # Generate a story from the last 5 commits
        story = generator.generate(limit=5)
        print("\n=== Code Evolution Narrative ===\n")
        print(story)
        print("\n=== End of Story ===")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
