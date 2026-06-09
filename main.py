import io
import json
import sys
from rich.console import Console
from modules.ownership_intelligence import run_ownership_intelligence, display_ownership_report
from modules.dependency_intelligence import run_dependency_intelligence, display_dependency_report
from modules.risk_intelligence import run_risk_intelligence, display_risk_report
from modules.recommendation_engine import generate_recommendations, display_recommendation_report
from modules.whatif_simulation import run_whatif_simulation, display_whatif_report
from modules.human_agent_map import run_human_agent_map, display_human_agent_map

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

    console.print("\n" + "-" * 60 + "\n")

    # Module 3
    risk_results, health_score = run_risk_intelligence(DATA_PATH)
    display_risk_report(risk_results, health_score, data["company"])

    console.print("\n" + "-" * 60 + "\n")

    # Module 4
    recommendations = generate_recommendations(risk_results, data)
    display_recommendation_report(recommendations, risk_results, health_score, data["company"])

    console.print("\n" + "-" * 60 + "\n")

    # Module 5
    scenarios, baseline_health = run_whatif_simulation(DATA_PATH)
    display_whatif_report(scenarios, baseline_health, data["company"])

    console.print("\n" + "-" * 60 + "\n")

    # Module 6
    profiles, gaps, results = run_human_agent_map(DATA_PATH)
    display_human_agent_map(profiles, gaps, results, data["company"])

    console.print("\n=== OBA Core Analysis Complete ===\n")


if __name__ == "__main__":
    main()