# make_backups.py
# Run this ONCE to pre-generate backup grids: py -3.13 make_backups.py
# Produces backup_grids.json with 3 filled grids per tier.

import json
from generate_grid import make_filled_grid, get_pattern


def generate_backups(n, target_blocks, count, time_limit=30):
    print("FILE IS RUNNING")
    """Generate `count` filled grids for a given size/block-count."""
    grids = []
    attempts = 0
    max_attempts = count * 30          # cap total tries so it can't run forever
    while len(grids) < count and attempts < max_attempts:
        attempts += 1
        print(f"  {n}x{n}: trying (have {len(grids)}/{count})...")
        grid, slots = make_filled_grid(n, target_blocks, time_limit=time_limit)
        if grid is not None:
            grids.append({
                "grid": grid,
                # store slots in a plain, JSON-friendly form (cells as lists, not tuples)
                "slots": [
                    {"direction": s["direction"], "cells": [list(c) for c in s["cells"]]}
                    for s in slots
                ]
            })
            print(f"  {n}x{n}: SUCCESS ({len(grids)}/{count})")
    return grids


if __name__ == "__main__":
    print("Generating backup grids (this will take a few minutes)...")

    backups = {
        "bitsize": generate_backups(5, 4, 3),
        "mega":    generate_backups(7, 8, 3),
        "giga":    generate_backups(10, 24, 3),
    }

    with open("backup_grids.json", "w") as f:
        json.dump(backups, f)

    # report what we actually got (some tiers might get fewer if generation is hard)
    print("\nDone. Saved backup_grids.json")
    for tier, grids in backups.items():
        print(f"  {tier}: {len(grids)} grids")