"""Generate all Phase 3 spell JSON outputs under data/."""

from parsers.spells import write_phase3_outputs


if __name__ == "__main__":
    counts = write_phase3_outputs("data")
    print("Generated Phase 3 outputs:")
    for name, count in counts.items():
        print(f"- {name}: {count}")
