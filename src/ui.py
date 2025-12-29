from typing import Dict, Any

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(title: str) -> None:
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {title} ==={Colors.ENDC}\n")

def print_commit(commit: Dict[str, Any]) -> None:
    hash_id = commit.get('hash', 'UNKNOWN')
    msg = commit.get('message', 'No message')
    insight = commit.get('insight', '')

    print(f"{Colors.YELLOW}Commit {hash_id}{Colors.ENDC}: {Colors.CYAN}{msg}{Colors.ENDC}")
    if insight:
        print(f"  {Colors.GREEN}-> {Colors.BOLD}Insight:{Colors.ENDC} {Colors.GREEN}{insight}{Colors.ENDC}")
    print() # Empty line for spacing

def print_error(message: str) -> None:
    print(f"{Colors.RED}{Colors.BOLD}Error:{Colors.ENDC} {message}")

def print_loading(message: str = "Generating narrative...") -> None:
    print(f"{Colors.BLUE}{message}{Colors.ENDC}", end="\r")
