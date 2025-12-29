import sys
from src.core.app import CodeChronicleApp

def main() -> None:
    # Use current directory by default if no path provided
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"Initializing CodeChronicle for: {repo_path}")

    try:
        app = CodeChronicleApp(repo_path)
        # Generate a story from the last 5 commits
        story = app.generate_narrative(limit=5)
        print("\n=== Code Evolution Narrative ===\n")
        print(story)
        print("\n=== End of Story ===")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()