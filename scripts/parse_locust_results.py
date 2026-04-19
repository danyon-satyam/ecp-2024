"""
Parse Locust CSV results and generate a performance summary report.

After running a Locust load test with --csv flag, this script
reads the results and prints a formatted performance report
suitable for including in your project documentation.

Usage:
  1. Run Locust with CSV output:
     locust -f tests/load/locustfile.py --host=http://127.0.0.1:8000 --headless --users 100 --spawn-rate 10 --run-time 60s --csv=tests/load/results/locust_results
     
  2. Parse the results:
     python scripts/parse_locust_results.py
"""
import sys
import os
import csv
from pathlib import Path

RESULTS_DIR = Path("tests/load/results")
STATS_FILE = RESULTS_DIR / "locust_results_stats.csv"


def parse_and_print_results() -> None:
    """Read Locust CSV output and print a formatted performance report."""
    if not STATS_FILE.exists():
        print(f"Results file not found: {STATS_FILE}")
        print("Run Locust with --csv=tests/load/results/locust_results first.")
        return

    print("\n" + "=" * 65)
    print("  STUDENT SENTIMENT API — LOAD TEST PERFORMANCE REPORT")
    print("=" * 65)

    with open(STATS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Print header
    print(f"\n{'Endpoint':<45} {'RPS':>6} {'Avg':>7} {'95%':>7} {'Fail%':>6}")
    print("-" * 75)

    total_requests = 0
    total_failures = 0

    for row in rows:
        if row["Name"] == "Aggregated":
            continue

        name = row["Name"][:44]
        rps = float(row.get("Requests/s", 0))
        avg = float(row.get("Average Response Time", 0))
        p95 = float(row.get("95%", 0))
        failures = int(row.get("Failure Count", 0))
        requests = int(row.get("Request Count", 0))
        fail_pct = (failures / requests * 100) if requests > 0 else 0

        total_requests += requests
        total_failures += failures

        print(
            f"{name:<45} {rps:>6.1f} {avg:>6.0f}ms {p95:>6.0f}ms "
            f"{fail_pct:>5.1f}%"
        )

    # Print aggregated summary
    print("-" * 75)
    for row in rows:
        if row["Name"] == "Aggregated":
            rps = float(row.get("Requests/s", 0))
            avg = float(row.get("Average Response Time", 0))
            p95 = float(row.get("95%", 0))
            overall_fail = (
                total_failures / total_requests * 100
                if total_requests > 0
                else 0
            )
            print(
                f"{'TOTAL':<45} {rps:>6.1f} {avg:>6.0f}ms "
                f"{p95:>6.0f}ms {overall_fail:>5.1f}%"
            )

    print(f"\nTotal Requests : {total_requests:,}")
    print(f"Total Failures : {total_failures:,}")
    print(
        f"Overall Failure Rate: "
        f"{(total_failures/total_requests*100):.2f}%"
        if total_requests > 0
        else "No requests recorded"
    )
    print("=" * 65 + "\n")


if __name__ == "__main__":
    parse_and_print_results()