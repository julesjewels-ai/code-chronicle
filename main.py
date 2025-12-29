import sys
import time
from src.core.app import CodeChronicleApp
from src.ui import print_header, print_commit, print_error, print_loading

def main() -> None:
    # Use current directory by default if no path provided
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print_header(f"CodeChronicle: {repo_path}")
    app = CodeChronicleApp(repo_path)

    try:
        loading_msg = "Generating narrative..."
        print_loading(loading_msg)

        # Generate a story from the last 5 commits
        events = app.get_narrative_events(limit=5)

        # Clear loading line dynamically
        print(" " * len(loading_msg) + "\r", end="")

        if not events:
            print("No commits found to chronicle.")
            return

        for event in events:
            print_commit(event)

        print("\n✅ Chronicle complete.")
    except Exception as e:
        print_error(str(e))

if __name__ == "__main__":
    main()