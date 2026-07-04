import random
import time

with open("2of12.txt") as f:
    words = [line.strip().upper() for line in f if len(line.strip()) >= 3]
#words- has all the words in our wordlist

words_set = set(words)   #set for O(1) validity lookups


#the index stores all the words by the length of the word
def build_length_index(words):
    index = {}
    for word in words:
        length = len(word)
        if length not in index:
            index[length] = []
        index[length].append(word)
    return index


#position-letter index-----for every (length, position, letter), store the SET of words
#that have that letter at that position. lets matches() intersect sets instead of scanning.
def build_position_index(words):
    index = {}
    for word in words:
        L = len(word)
        for pos, letter in enumerate(word):#enumerate tracks the position and letter in the word simulataneously
            key = (L, pos, letter)
            if key not in index:
                index[key] = set()
            index[key].add(word)
    return index
#so all the words with a certain length that has the letter letter in the pos position


#also keep words grouped by length, as a set, for patterns that are all wildcards
def build_length_sets(words):
    index = {}
    for word in words:
        L = len(word)
        if L not in index:
            index[L] = set()
        index[L].add(word)
    return index
# we need the set apart from the index so that we can apply the intersection operation 


length_index = build_length_index(words)
position_index = build_position_index(words)
length_sets = build_length_sets(words)


#matches now intersects the pattern and the words of that length/matching positions 
#instead of scanning every word of that length character-by-character
def matches(pattern):
    L = len(pattern)
    
    #collects the fixed positions, the ones which have letters filled in already 
    fixed = [(i, pattern[i]) for i in range(L) if pattern[i] != '_']
    #gets the index and the corresponding letter in the pattern 

    #if the pattern doesnt even have a single cell filled in, all the available wrods of this length qualify
    if not fixed:
        return list(length_sets.get(L, set()))

    
    result = None
    for (i, letter) in fixed:
        s = position_index.get((L, i, letter), set())
        if result is None:
            result = s
        else:
            result = result & s          #intersects with all the words that have word i in position i  
        if not result:                   #no matches for that word with those blanks 
            return []
    return list(result)


##Validation functions
##Validation function 1 - similar to leetcode island question- the entire
#crossword must be connected
def check_connectivity(grid):
    n = len(grid)
    visited = set()
    count = 0
    for i in range(n):
        for j in range(n):
            if grid[i][j] == '.' and (i, j) not in visited:
                count += 1
                explore(grid, i, j, visited)
    return count == 1


def explore(grid, i, j, visited):
    n = len(grid)
    if i < 0 or i >= n or j < 0 or j >= n:
        return
    if grid[i][j] != '.':
        return
    if (i, j) in visited:
        return
    visited.add((i, j))
    explore(grid, i + 1, j, visited)
    explore(grid, i - 1, j, visited)
    explore(grid, i, j + 1, visited)
    explore(grid, i, j - 1, visited)


#check that the white spaces have a minimum length of 3, both in the rows and columns
#minimum length of the word is 3, that is why
def check_min_length(grid):
    n = len(grid)
    for i in range(n):
        c = 0
        for j in range(n):
            if grid[i][j] == '.':
                c += 1
            else:
                if c == 1 or c == 2:
                    return False
                c = 0
        if c == 1 or c == 2:
            return False
    for j in range(n):
        c = 0
        for i in range(n):
            if grid[i][j] == '.':
                c += 1
            else:
                if c == 1 or c == 2:
                    return False
                c = 0
        if c == 1 or c == 2:
            return False
    return True


##grid generator
#uses backtracking to generate the crossword grid
#blocks places is the number of black square we want in our grid
def generate(grid, blocks_placed, target):
    n = len(grid)
    if blocks_placed >= target:
        if check_connectivity(grid) and check_min_length(grid):
            return True
        return False

    cells = [(r, c) for r in range(n) for c in range(n)]
    random.shuffle(cells)

    for (r, c) in cells:
        pr, pc = n - 1 - r, n - 1 - c
        if grid[r][c] == '.' and grid[pr][pc] == '.' and (r, c) != (pr, pc):
            grid[r][c] = '#'
            grid[pr][pc] = '#'
            if check_min_length(grid):
                if generate(grid, blocks_placed + 2, target):
                    return True
            grid[r][c] = '.'
            grid[pr][pc] = '.'
    return False


#functions to create and print grids
def make_empty_grid(n):
    return [['.' for _ in range(n)] for _ in range(n)]


def print_grid(grid):
    for row in grid:
        print(" ".join(row))
    print()


def extract_slots(grid):
    n = len(grid)
    slots = []
    for r in range(n):
        c = 0
        while c < n:
            if grid[r][c] == '.':
                cells = []
                while c < n and grid[r][c] == '.':
                    cells.append((r, c))
                    c += 1
                slots.append({"direction": "across", "cells": cells})
            else:
                c += 1
    for c in range(n):
        r = 0
        while r < n:
            if grid[r][c] == '.':
                cells = []
                while r < n and grid[r][c] == '.':
                    cells.append((r, c))
                    r += 1
                slots.append({"direction": "down", "cells": cells})
            else:
                r += 1
    return slots


def get_pattern(grid, slot):
    pattern = ""
    for (r, c) in slot["cells"]:
        if grid[r][c] == '.':
            pattern += '_'
        else:
            pattern += grid[r][c]
    return pattern


#counts how many words are there in that corresponding cell ( that can be 1 or 2), so that we backtrack according to the frequency  
def make_count_grid(n):
    return [[0 for _ in range(n)] for _ in range(n)]


def place_word(grid, counts, slot, word):
    for (r, c), letter in zip(slot["cells"], word):
        grid[r][c] = letter
        counts[r][c] += 1


def remove_word(grid, counts, slot, word):
    for (r, c) in slot["cells"]:
        counts[r][c] -= 1
        if counts[r][c] == 0:
            grid[r][c] = '.'


#The backtracking function to fill all the slots in the grid with words from the wordlist
def fill(grid, counts, slots, used, start_time, limit):
    if time.time() - start_time > limit:
        return None

    unfilled = [s for s in slots if '_' in get_pattern(grid, s)]

    if not unfilled:
        for s in slots:
            if get_pattern(grid, s) not in words_set:
                return False
        return True

    best_slot = None
    best_candidates = None
    for s in unfilled:
        candidates = matches(get_pattern(grid, s))   #now uses the fast position index
        if len(candidates) == 0:
            return False
        if best_candidates is None or len(candidates) < len(best_candidates):
            best_slot = s
            best_candidates = candidates

    random.shuffle(best_candidates)

    for word in best_candidates:
        if word in used:
            continue
        place_word(grid, counts, best_slot, word)
        used.add(word)
        result = fill(grid, counts, slots, used, start_time, limit)
        if result is True:
            return True
        if result is None:
            remove_word(grid, counts, best_slot, word)
            used.discard(word)
            return None
        remove_word(grid, counts, best_slot, word)
        used.discard(word)

    return False

#turns a grid into a hashable string so we can detect duplicate patterns
def grid_to_key(grid):
    return "".join("".join(row) for row in grid)


#to make the filled grid using the functions given above 
def make_filled_grid(n, target_blocks, time_limit=5, max_attempts=40):
    seen = set()
    for _ in range(max_attempts):
        grid = make_empty_grid(n)
        if not generate(grid, 0, target_blocks):
            continue
        key = grid_to_key(grid)
        if key in seen:
            continue
        seen.add(key)
        slots = extract_slots(grid)
        counts = make_count_grid(n)
        used = set()
        if fill(grid, counts, slots, used, time.time(), time_limit) is True:
            return grid, slots
    return None, None



#tester
N = 10
TARGET_BLOCKS = 24
TIME_LIMIT = 5
MAX_ATTEMPTS = 40

solved = False
seen_grids = set()  #grid patterns we've already tried
consecutive_dupes = 0       #how many times in a row we've generated a repeat
DUPE_LIMIT = 200 #if we can't find a NEW grid after this many tries, give up


if __name__ == "__main__":
    for attempt in range(MAX_ATTEMPTS):
        #try to generate a NEW (unseen) grid; give up if we keep getting duplicates
        grid = None
        while consecutive_dupes < DUPE_LIMIT:
            candidate = make_empty_grid(N)
            if not generate(candidate, 0, TARGET_BLOCKS):
                continue
            key = grid_to_key(candidate)
            if key in seen_grids:
                consecutive_dupes += 1        #generated a repeat
                continue
            #found a fresh grid
            seen_grids.add(key)
            consecutive_dupes = 0
            grid = candidate
            break

        #if we couldn't find any new grid, stop entirely
        if grid is None:
            print(f"Ran out of new grids to try after {attempt} attempts.")
            break

        slots = extract_slots(grid)
        counts = make_count_grid(N)
        used = set()
        t0 = time.time()
        result = fill(grid, counts, slots, used, time.time(), TIME_LIMIT)
        print(f"attempt {attempt+1}: {time.time()-t0:.1f}s, result={result}", flush=True)

        #print the grid every time (solved or not), as requested
        print_grid(grid)

        if result is True:
            print(f"Solved on attempt {attempt+1} — {N}x{N} grid, {len(slots)} words:")
            for slot in slots:
                w = get_pattern(grid, slot)
                if w not in words_set:
                    print("INVALID WORD:", w, slot["direction"])
            solved = True
            break

    if not solved:
        print(f"Could not fill any grid.")
# import random
# import time
# from index_generator import build_length_index, matches, words

# with open("2of12.txt") as f:
#     words = [line.strip().upper() for line in f if len(line.strip()) >= 3]
# #words- has all the words in our wordlist 

# words_set = set(words)   #set for O(1) validity lookups (list lookup was O(n))
# length_index = build_length_index(words)

# ##Validation functions 
# ##Validation function 1 - similar to leetcode island question- the entire 
# #crossword must be connected 
# def check_connectivity(grid):
#     n = len(grid)
#     visited = set()
#     count = 0
#     for i in range(n):
#         for j in range(n):
#             if grid[i][j] == '.' and (i, j) not in visited:
#                 count += 1
#                 explore(grid, i, j, visited)
#     return count == 1


# def explore(grid, i, j, visited):
#     n = len(grid)
#     if i < 0 or i >= n or j < 0 or j >= n:
#         return
#     if grid[i][j] != '.':
#         return
#     if (i, j) in visited:
#         return
#     visited.add((i, j))
#     explore(grid, i + 1, j, visited)
#     explore(grid, i - 1, j, visited)
#     explore(grid, i, j + 1, visited)
#     explore(grid, i, j - 1, visited)

# #check that the white spaces have a minimum length of 3, both in the rows and columns 
# #minimum length of the word is 3, that is why
# def check_min_length(grid):
#     n = len(grid)
#     for i in range(n):
#         c = 0
#         for j in range(n):
#             if grid[i][j] == '.':
#                 c += 1
#             else:
#                 if c == 1 or c == 2:
#                     return False
#                 c = 0
#         if c == 1 or c == 2:
#             return False
#     for j in range(n):
#         c = 0
#         for i in range(n):
#             if grid[i][j] == '.':
#                 c += 1
#             else:
#                 if c == 1 or c == 2:
#                     return False
#                 c = 0
#         if c == 1 or c == 2:
#             return False
#     return True


# ##grid generator 
# #uses backtracking to generate the crossword grid 
# #blocks places is the number of black square we want in our grid 
# def generate(grid, blocks_placed, target):
#     n = len(grid)
#     #if we have placed all the blocks, and the grid is connected, we can use it
#     if blocks_placed >= target:
#         if check_connectivity(grid) and check_min_length(grid):
#             return True
#         return False

#     #tried generating in order-puzzles were too uniform, so I tried to just generate random cells, 
#     # place them and their mirror in the grid, and check if it breaks min length 
#     cells = [(r, c) for r in range(n) for c in range(n)]
#     random.shuffle(cells)

#     for (r, c) in cells:
#         pr, pc = n - 1 - r, n - 1 - c  #the partner, the symmetric cell 
#         if grid[r][c] == '.' and grid[pr][pc] == '.' and (r, c) != (pr, pc):
#             grid[r][c] = '#'
#             grid[pr][pc] = '#'
#             #if the current grid satisfies the min length, then we go deeper into that branch 
#             #if at the end of that branch, there is a valid grid, we return true 
#             if check_min_length(grid):
#                 if generate(grid, blocks_placed + 2, target):
#                     return True
#             #if there is no vaild grid at the end of the branch, we backtrack
#             grid[r][c] = '.'
#             grid[pr][pc] = '.'
#     #if we cant find any valid pair, then it is false, we cannot place anymore pairs that doesn't break the min length rule  
#     #then we return false 
#     return False


# #functions to create and print grids  
# def make_empty_grid(n):
#     return [['.' for _ in range(n)] for _ in range(n)]


# def print_grid(grid):
#     for row in grid:
#         print(" ".join(row))
#     print()


# def extract_slots(grid):
#     n = len(grid)
#     slots = []

#     # ---------- ACROSS (scan each row left-to-right) ----------
#     for r in range(n):
#         c = 0
#         while c < n:
#             if grid[r][c] == '.':
#                 cells = []
#                 while c < n and grid[r][c] == '.':
#                     cells.append((r, c))
#                     c += 1
#                 slots.append({"direction": "across", "cells": cells})
#             else:
#                 c += 1

#     # ---------- DOWN (scan each column top-to-bottom) ----------
#     for c in range(n):
#         r = 0
#         while r < n:
#             if grid[r][c] == '.':
#                 cells = []
#                 while r < n and grid[r][c] == '.':
#                     cells.append((r, c))
#                     r += 1
#                 slots.append({"direction": "down", "cells": cells})
#             else:
#                 r += 1

#     return slots

# def get_pattern(grid, slot):
#     pattern = ""
#     for (r, c) in slot["cells"]:
#         if grid[r][c] == '.':
#             pattern += '_'
#         else:
#             pattern += grid[r][c]
#     return pattern

# #counts how many placed words use each cell (1 or 2), so backtracking only clears a cell when no word needs it
# def make_count_grid(n):
#     return [[0 for _ in range(n)] for _ in range(n)]

# def place_word(grid, counts, slot, word):
#     for (r, c), letter in zip(slot["cells"], word):
#         grid[r][c] = letter
#         counts[r][c] += 1

# def remove_word(grid, counts, slot, word):
#     for (r, c) in slot["cells"]:
#         counts[r][c] -= 1
#         #only clear the cell if no other word still uses it
#         if counts[r][c] == 0:
#             grid[r][c] = '.'

# #The backtracking function to fill all the slots in the grid 
# #with words from the wordlist 
# #start_time and limit added so a hard grid is abandoned instead of hanging forever
# def fill(grid, counts, slots, length_index, used, start_time, limit):
#     #if we have spent too long on this grid, give up so the caller can try a fresh grid
#     if time.time() - start_time > limit:
#         return None    #None signals "timed out", different from False ("this branch failed")

#     #slots that still have an empty cell left in them, so they are unfilled
#     unfilled = [s for s in slots if '_' in get_pattern(grid, s)]

#     #if the unfilled is empty, the grid is complete, and all the words are valid 
#     if not unfilled:
#         for s in slots:
#             if get_pattern(grid, s) not in words_set:   #set lookup, O(1)
#                 return False
#         return True

#     #Picking the best slot  to fill- it is the one with least options that can fit it 
#     best_slot = None
#     best_candidates = None
#     for s in unfilled:
#         candidates = matches(get_pattern(grid, s), length_index)#all the candidates for that slot, using the index
#         #early failure: a slot with zero options means this branch is dead, stop looking
#         if len(candidates) == 0:
#             return False
#         if best_candidates is None or len(candidates) < len(best_candidates):#taking the slot with the least amount of candidates
#             best_slot = s
#             best_candidates = candidates
#     #best slot is the slot, and best candidates are the corresponding candidates word 

#     #shuffle so each run produces a different fill, not the same alphabetical-first solution
#     best_candidates = list(best_candidates)
#     random.shuffle(best_candidates)

#     #From teh selected slot, pick the each candidate, and keep going deeper into the same branch, if at any point it fails, then we backtrack the current step
#     for word in best_candidates:
#         if word in used:                 #don't use the same word twice
#             continue
#         place_word(grid, counts, best_slot, word)
#         used.add(word)
#         result = fill(grid, counts, slots, length_index, used, start_time, limit)
#         if result is True:
#             return True
#         if result is None:               #timed out — unwind and report up
#             remove_word(grid, counts, best_slot, word)
#             used.discard(word)
#             return None
#         #backtrack that means this branch is invalid 
#         remove_word(grid, counts, best_slot, word)
#         used.discard(word)

#     return False    

# #tester
# #try to generate AND fill; if filling times out or fails, throw the grid away and try a fresh one
# N = 7
# TARGET_BLOCKS = 4
# TIME_LIMIT = 10        #seconds allowed per grid before giving up on it
# MAX_ATTEMPTS = 10     #how many fresh grids to try before admitting defeat

# solved = False
# for attempt in range(MAX_ATTEMPTS):
#     grid = make_empty_grid(N)
#     success = generate(grid, 0, TARGET_BLOCKS)
#     if not success:
#         continue

#     slots = extract_slots(grid)
#     counts = make_count_grid(N)
#     used = set()
#     result = fill(grid, counts, slots, length_index, used, time.time(), TIME_LIMIT)

#     if result is True:
#         print(f"Solved on attempt {attempt+1} — valid {N}x{N} grid with {TARGET_BLOCKS} black squares:")
#         print("Number of words:", len(slots))
#         print("\nFilled grid:")
#         print_grid(grid)
#         for slot in slots:
#             w = get_pattern(grid, slot)
#             if w not in words_set:
#                 print("INVALID WORD:", w, slot["direction"])
#         solved = True
#         break
#     #else: timed out or unfillable -> loop tries a brand new grid

# if not solved:
#     print(f"Could not fill any grid in {MAX_ATTEMPTS} attempts.")