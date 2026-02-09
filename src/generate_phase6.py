"""Generate Phase 6 outputs under data/."""

from parsers.phase6_core import write_phase6_outputs


if __name__ == "__main__":
    summary = write_phase6_outputs("data")
    print("Generated Phase 6 outputs:")
    for k, v in summary.items():
        print(f"- {k}: {v}")
