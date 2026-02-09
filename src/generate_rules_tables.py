"""Generate all Phase 2 JSON outputs under data/."""

from parsers.rules_tables import write_phase2_outputs


if __name__ == "__main__":
    counts = write_phase2_outputs("data")
    print("Generated Phase 2 outputs:")
    for name, count in counts.items():
        print(f"- {name}: {count}")
