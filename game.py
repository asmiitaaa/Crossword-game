from generate_grid import make_filled_grid, get_pattern
from clue_generator import generate_clue
from warmth import warmth

#tier settings: (grid size, target black squares)
N = 5
TARGET_BLOCKS = 4


#builds the display grid: '#' for black, letters for solved cells, '_' for empty
def build_display(grid, slots, solved):
    n = len(grid)
    display = [['#' if grid[r][c] == '#' else '_' for c in range(n)] for r in range(n)]
    for idx in solved:
        answer = get_pattern(grid, slots[idx])
        for (r, c), letter in zip(slots[idx]["cells"], answer):
            display[r][c] = letter
    return display


#prints the grid with row/column numbers
def print_puzzle(display):
    n = len(display)
    print("\n  " + " ".join(str(c) for c in range(n)))
    for r in range(n):
        print(f"{r} " + " ".join(display[r]))
    print()


#reads a slot's current pattern from the DISPLAY grid (what the player has filled so far)
def slot_pattern(display, slot):
    return "".join(display[r][c] for (r, c) in slot["cells"])


#the puzzle is complete when no white cell is still empty
def puzzle_complete(display):
    for row in display:
        if '_' in row:
            return False
    return True


print("Generating your crossword... (this takes a moment)")
grid, slots = make_filled_grid(N, TARGET_BLOCKS)

if grid is None:
    print("Couldn't generate a puzzle. Try running again.")
    exit()

#the correct answer for each slot, read from the filled solution grid
answers = [get_pattern(grid, s) for s in slots]

#generate a clue for each answer
print("Writing clues...")
clues = [generate_clue(ans) for ans in answers]

#show the puzzle
print("\n===== CROSSWORD =====")
for i, (slot, clue) in enumerate(zip(slots, clues)):
    length = len(slot["cells"])
    print(f"{i+1}. ({slot['direction']}, {length} letters) {clue}")

solved = set()

#game loop
while True:
    display = build_display(grid, slots, solved)

    #auto-solve any slot whose cells are now all filled by crossing words
    for i, slot in enumerate(slots):
        if i not in solved and '_' not in slot_pattern(display, slot):
            solved.add(i)

    #rebuild display in case auto-solving added anything
    display = build_display(grid, slots, solved)

    #check if the whole puzzle is complete
    if puzzle_complete(display):
        print_puzzle(display)
        print("You solved the whole crossword! 🎉")
        break

    print(f"\nSolved {len(solved)}/{len(slots)}")
    print_puzzle(display)

    choice = input("Pick a clue number (or 'q' to quit): ").strip()
    if choice == 'q':
        print("Thanks for playing!")
        break
    if not choice.isdigit():
        print("Enter a number.")
        continue
    idx = int(choice) - 1
    if idx < 0 or idx >= len(slots):
        print("That clue number doesn't exist.")
        continue
    if idx in solved:
        print("You already solved that one.")
        continue

    guess = input("Your guess: ").strip().upper()
    answer = answers[idx]
    feedback = warmth(clues[idx], guess, answer)
    print(f">>> {feedback}")
    if guess == answer:
        solved.add(idx)
        print(f"Correct! It was {answer}.")