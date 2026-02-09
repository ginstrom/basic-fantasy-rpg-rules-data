"""Generate Phase 5 outputs under data/."""

from parsers.phase5_treasure import write_phase5_outputs


if __name__ == "__main__":
    summary = write_phase5_outputs("data")
    print("Generated Phase 5 outputs:")
    for k, v in summary.items():
        print(f"- {k}: {v}")
