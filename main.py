import io
import json
import sys
from rich.console import Console
from modules.ownership_intelligence import run_ownership_intelligence, display_ownership_report
from modules.dependency_intelligence import run_dependency_intelligence, display_dependency_report

# Force UTF-8 output on Windows to avoid cp1252 encoding errors
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console(file=sys.stdout, force_terminal=True, highlight=False)

DATA_PATH = "data/sunrise_care.json"

def main():
    with open(DATA_PATH) as f:
        data = json.load(f)

    console.print("\n=== OBA CORE - AI WORKFORCE INTELLIGENCE ===\n")

    # Module 1
    ownership_results = run_ownership_intelligence(DATA_PATH)
    display_ownership_report(ownership_results, data["company"])

    console.print("\n" + "-" * 60 + "\n")

    # Module 2
    dependency_results = run_dependency_intelligence(DATA_PATH)
    display_dependency_report(dependency_results, data)

    console.print("\n=== Analysis Complete ===\n")


if __name__ == "__main__":
    main()
