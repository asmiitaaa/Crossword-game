# ---------- grid helpers ----------
def print_grid(grid):
    for row in grid:
        print(" ".join(row))
    print()


# ---------- connectivity check (flood-fill) ----------
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
    if i < 0 or i >= n or j < 0 or j >= n:   # out of bounds
        return
    if grid[i][j] != '.':                     # black square
        return
    if (i, j) in visited:                     # already counted
        return
    visited.add((i, j))
    explore(grid, i + 1, j, visited)
    explore(grid, i - 1, j, visited)
    explore(grid, i, j + 1, visited)
    explore(grid, i, j - 1, visited)


# ---------- minimum slot length check ----------
def check_min_length(grid):
    n = len(grid)

    # --- check each ROW (across slots) ---
    for i in range(n):
        c = 0
        for j in range(n):
            if grid[i][j] == '.':      # white: extend the run
                c += 1
            else:                       # black: run ended, check it
                if c == 1 or c == 2:
                    return False
                c = 0
        if c == 1 or c == 2:            # run that ended at the row's edge
            return False

    # --- check each COLUMN (down slots) ---
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


# ---------- test grids ----------
grid_connected = [
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
]

grid_disconnected = [
    ['.', '#', '.', '#', '.'],
    ['#', '#', '.', '#', '#'],
    ['.', '.', '.', '.', '.'],
    ['#', '#', '.', '#', '#'],
    ['.', '#', '.', '#', '.'],
]

grid_corners = [
    ['#', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '#'],
]

# short runs (length-2) created by center blocks -> should FAIL min-length
grid_short = [
    ['.', '.', '#', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '#', '.', '.'],
]


# ---------- run tests ----------
print("Connected grid:")
print_grid(grid_connected)
print("check_connectivity ->", check_connectivity(grid_connected))   # expect True
print("check_min_length   ->", check_min_length(grid_connected))     # expect True
print()

print("Disconnected grid:")
print_grid(grid_disconnected)
print("check_connectivity ->", check_connectivity(grid_disconnected))  # expect False
print()

print("Corner-blocks grid:")
print_grid(grid_corners)
print("check_connectivity ->", check_connectivity(grid_corners))     # expect True
print("check_min_length   ->", check_min_length(grid_corners))       # expect True
print()

print("Short-run grid:")
print_grid(grid_short)
print("check_min_length   ->", check_min_length(grid_short))         # expect False