from flask import Flask, render_template, request, jsonify
from generate_grid import make_filled_grid, get_pattern
from clue_generator import generate_clue
from warmth import warmth
import json, random

app = Flask(__name__)

# load the pre-generated backup grids (fallback when live generation fails)
with open("backup_grids.json") as f:
    BACKUPS = json.load(f)



# holds the current game state (single-game version)
game = {}


# serves the main page
@app.route("/")
def index():
    return render_template("index.html")


# starts a new game: generates a grid + clues, returns them to the browser
# per-tier generation limits: (grid size, blocks, time_limit_per_attempt, max_attempts)
TIER_GEN = {
    "bitsize": (5, 4, 5, 4),    # 5x5: solves instantly, short window
    "mega":    (7, 8, 5, 5),    # 7x7: usually fast
    "giga":    (10, 24, 5, 6),  # 10x10: up to 30s (5s x 6), then backup
}

@app.route("/new_game")
def new_game():
    tier = request.args.get("tier", "bitsize")
    n, blocks, tlimit, attempts = TIER_GEN[tier]

    grid, slots = make_filled_grid(n, blocks, time_limit=tlimit, max_attempts=attempts)
    if grid is None:
        entry = random.choice(BACKUPS[tier])
        grid = entry["grid"]
        slots = entry["slots"]

    # ... rest stays the same (answers, clues, etc.)

    # read the answer for each slot from the filled grid
    answers = [get_pattern(grid, s) for s in slots]
    # generate a clue for each answer
    clues = [generate_clue(a) for a in answers]

    # store answers + clues SERVER-SIDE (never sent to the browser, so no cheating)
    game["answers"] = answers
    game["clues"] = clues
    game["slots"] = slots
    game["size"] = n

    # build a simple black-square map to send to the browser (1 = black, 0 = white)
    black = [[1 if grid[r][c] == '#' else 0 for c in range(n)] for r in range(n)]

    # send the grid shape + clues + slot positions (but NOT the answers)
    return jsonify({
        "size": n,
        "black": black,
        "clues": clues,
        "slots": [
            {"direction": s["direction"], "cells": [list(c) for c in s["cells"]]}
            for s in slots
        ]
    })


# checks a guess against the stored answer, returns warm/cold feedback
@app.route("/guess", methods=["POST"])
def guess():
    data = request.json
    idx = data["clue_index"]
    g = data["guess"].strip().upper()
    answer = game["answers"][idx]
    feedback = warmth(game["clues"][idx], g, answer)
    return jsonify({
        "feedback": feedback,
        "correct": (g == answer)
    })

@app.route("/hint")
def hint():
    idx = int(request.args.get("clue_index"))
    pos = int(request.args.get("pos", 0))
    answer = game["answers"][idx]
    if pos < 0 or pos >= len(answer):
        pos = 0
    return jsonify({"pos": pos, "letter": answer[pos]})

if __name__ == "__main__":
    app.run(debug=True)