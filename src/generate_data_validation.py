"""Run Phase 7 validation/cleanup/docs generation."""

from parsers.data_validation import run_phase7


if __name__ == "__main__":
    summary = run_phase7("data")
    print("Phase 7 summary:")
    for k, v in summary.items():
        print(f"- {k}: {v}")
