"""Generate Phase 4 monster output under data/."""

from parsers.phase4_monsters import write_phase4_output


if __name__ == "__main__":
    summary = write_phase4_output("data")
    print("Generated Phase 4 outputs:")
    for k, v in summary.items():
        print(f"- {k}: {v}")
