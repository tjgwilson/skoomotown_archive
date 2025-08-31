import random
import time
from typing import List, Set, Tuple

from blessed import Terminal
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from utility.intro import show_module_intro

console = Console()
term = Terminal()

# Configuration constants
GRID_SIZE: int = 5
TRAP_COUNT: int = 3
TIME_LIMIT: float = 120.0  # seconds for puzzle
ALERT_THRESHOLD: int = 1  # max traps before failure

# Glitch effect constants
GLITCH_FRAMES: int = 6
GLITCH_DELAY: float = 0.05
GLITCH_CHARS: str = '░▒▓█<>*'

# Beep intervals
INITIAL_BEEP_INTERVAL: float = 10.0  # start interval
MIN_BEEP_INTERVAL: float = 0.2       # fastest beep

# Tile rotation mapping (90° clockwise)
ROTATION_MAP = {
    '─': '│', '│': '─',
    '┌': '┐', '┐': '┘',
    '┘': '└', '└': '┌',
    '┬': '┤', '┤': '┴',
    '┴': '├', '├': '┬',
    '┼': '┼'
}

# Connectivity for tiles
CONNECTIONS = {
    '─': {'W', 'E'}, '│': {'N', 'S'},
    '┌': {'E', 'S'}, '┐': {'W', 'S'},
    '┘': {'W', 'N'}, '└': {'E', 'N'},
    '┬': {'W', 'E', 'S'}, '┴': {'W', 'E', 'N'},
    '├': {'N', 'S', 'E'}, '┤': {'N', 'S', 'W'},
    '┼': {'N', 'E', 'S', 'W'}
}

# Available tile types
TILES: List[str] = list(CONNECTIONS.keys())
ENTRY: Tuple[int, int] = (0, 0)
EXIT: Tuple[int, int] = (GRID_SIZE - 1, GRID_SIZE - 1)


def glitch_effect(frames: int = GLITCH_FRAMES,
                  delay: float = GLITCH_DELAY) -> None:
    """Display a red glitch animation on detection."""
    width = term.width or GRID_SIZE
    height = (term.height or GRID_SIZE * 2) // 4
    for _ in range(frames):
        print(term.clear())
        for _ in range(height):
            line = ''.join(random.choice(GLITCH_CHARS)
                           for _ in range(width))
            console.print(Text(line, style='bold red'))
        time.sleep(delay)
    print(term.clear())


def draw_status(traps_hit: int, remaining: float) -> None:
    """Render the top status bar: time remaining and traps triggered."""
    traps_bar = '■' * traps_hit + '·' * (ALERT_THRESHOLD - traps_hit)
    panel = Panel(
        Text.assemble(
            (' TIME ', 'bold white on black'),
            (f'{remaining:0.1f}s ', 'bold cyan'),
            (' TRAP ', 'bold white on black'), (traps_bar, 'bold red')
        ),
        title='Circuit Override Status',
        border_style='white'
    )
    console.print(panel)


def print_grid(grid: List[List[str]]) -> None:
    """Display the grid with row and column labels."""
    table = Table(show_header=True, header_style='bold')
    table.add_column(' ', width=2)
    for col_index in range(1, GRID_SIZE + 1):
        table.add_column(str(col_index), justify='center')

    for row_index in range(GRID_SIZE):
        row_cells: List[Text] = [Text(str(row_index + 1))]
        for col_index in range(GRID_SIZE):
            position = (row_index, col_index)
            if position == ENTRY:
                cell = Text('E', style='bold green')
            elif position == EXIT:
                cell = Text('X', style='bold magenta')
            else:
                cell = Text(grid[row_index][col_index])
            row_cells.append(cell)
        table.add_row(*row_cells)
    console.print(table)


def rotate_tile(grid: List[List[str]], row: int, col: int) -> None:
    """
    Rotate the tile at (row, col) 90° clockwise.

    :param grid: Current tile grid.
    :param row: Zero-based row index.
    :param col: Zero-based column index.
    """
    grid[row][col] = ROTATION_MAP.get(grid[row][col], grid[row][col])


def is_solved(grid: list[list[str]],
              traps: set[tuple[int, int]]) -> bool:
    """
    Return True if a valid path connects ENTRY to EXIT avoiding traps.

    ENTRY/EXIT are treated as 'wildcards' that can connect on any side so
    the player doesn't have to rotate those hidden tiles.

    :param grid: Current tile grid.
    :param traps: Set of trap coordinates.
    :return: Whether the puzzle is solved.
    """
    visited: set[tuple[int, int]] = set()
    stack: list[tuple[int, int]] = [ENTRY]
    opposite = {'N': 'S', 'S': 'N', 'W': 'E', 'E': 'W'}
    all_dirs = {'N', 'S', 'E', 'W'}

    while stack:
        row, col = stack.pop()
        if (row, col) in visited or (row, col) in traps:
            continue
        visited.add((row, col))
        if (row, col) == EXIT:
            return True

        # Current tile directions (wildcard at endpoints)
        if (row, col) in (ENTRY, EXIT):
            dirs_here = all_dirs
        else:
            dirs_here = CONNECTIONS[grid[row][col]]

        for direction in dirs_here:
            new_row = row + (direction == 'S') - (direction == 'N')
            new_col = col + (direction == 'E') - (direction == 'W')
            if not (0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE):
                continue

            # Neighbour directions (also wildcard if neighbour is an endpoint)
            if (new_row, new_col) in (ENTRY, EXIT):
                neighbour_dirs = all_dirs
            else:
                neighbour_dirs = CONNECTIONS[grid[new_row][new_col]]

            if opposite[direction] in neighbour_dirs:
                stack.append((new_row, new_col))

    return False


# -------------------- NEW HELPERS (ensure solvable) --------------------

def _build_solution_path() -> List[Tuple[int, int]]:
    """
    Create a monotone (right/down) path from ENTRY to EXIT.

    :return: List of coordinates from ENTRY to EXIT inclusive.
    """
    path: List[Tuple[int, int]] = [ENTRY]
    r, c = ENTRY
    while (r, c) != EXIT:
        can_down = r < GRID_SIZE - 1
        can_right = c < GRID_SIZE - 1
        if can_down and (not can_right or random.choice([True, False])):
            r += 1
        else:
            c += 1
        path.append((r, c))
    return path


def _place_solution_tiles(grid: List[List[str]],
                          path: List[Tuple[int, int]]) -> None:
    """
    Place tiles so that their connection sets are supersets of neighbours.

    This guarantees the path is realisable (even at endpoints where no tile
    has a single-connection degree).

    :param grid: Grid to mutate in-place.
    :param path: Coordinates of the intended solution path.
    """
    deltas = {(-1, 0): 'N', (1, 0): 'S', (0, -1): 'W', (0, 1): 'E'}

    for pr, pc in path:
        # Which directions along the path touch this cell?
        neighbours: Set[str] = set()
        for (dr, dc), d in deltas.items():
            if (pr + dr, pc + dc) in path:
                neighbours.add(d)

        # Choose a tile whose connections are a *superset* of neighbours,
        # preferring the smallest (fewest extraneous arms).
        candidates = [
            (tile, conns) for tile, conns in CONNECTIONS.items()
            if neighbours.issubset(conns)
        ]
        # Sort by connection count ascending (2, then 3, then 4)
        candidates.sort(key=lambda x: len(x[1]))
        chosen = candidates[0][0] if candidates else '┼'
        grid[pr][pc] = chosen


# -------------------- MAIN GAME --------------------

def circuit_override() -> bool:
    """
    Execute the circuit override puzzle with continuous timer.

    Ensures there is at least one valid solution by:
    1) Building a path,
    2) Laying compatible tiles (superset connections),
    3) Verifying solvable before scrambling,
    4) Scrambling via rotations (and ensuring start state isn't already solved).

    :return: True on success, False on failure or abort.
    """
    # 1) Build solution path
    solution_path = _build_solution_path()

    # 2) Place traps off the path
    all_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
    off_path = [pos for pos in all_cells if pos not in solution_path]
    traps = set(random.sample(off_path, k=min(TRAP_COUNT, len(off_path))))

    # 3) Initialise grid and lay solution tiles
    grid = [[random.choice(TILES) for _ in range(GRID_SIZE)]
            for _ in range(GRID_SIZE)]
    _place_solution_tiles(grid, solution_path)

    # 4) Verify the *constructed* grid is solvable (pre-scramble)
    assert is_solved(grid, traps), "Internal error: constructed grid not solvable"

    # 5) Scramble by rotating each tile 0–3 times
    for r_idx in range(GRID_SIZE):
        for c_idx in range(GRID_SIZE):
            turns = random.randint(0, 3)
            for _ in range(turns):
                grid[r_idx][c_idx] = ROTATION_MAP[grid[r_idx][c_idx]]

    # Optional: ensure we don't start already solved (gives the player work)
    if is_solved(grid, traps):
        # Rotate a random non-start/non-end tile once to break solution
        breakable = [pos for pos in solution_path if pos not in (ENTRY, EXIT)]
        if breakable:
            br, bc = random.choice(breakable)
            grid[br][bc] = ROTATION_MAP[grid[br][bc]]

    # Intro sequence
    show_module_intro(
        "Protocol Gamma: Circuit Override",
        "- Rotate tiles to form a path from [green]E[/green] to [magenta]X[/magenta].\n"
        "- Avoid the wizard-hidden traps (they flash briefly at start).\n"
        "- Complete within 120 seconds."
    )

    # Reveal traps briefly
    print(term.clear())
    console.print(Text("-- SYSTEM ALERT: TRAP NODES DETECTED --",
                       style='bold yellow'))
    table = Table(show_header=True, header_style='bold red')
    table.add_column(' ', width=2)
    for col_idx in range(1, GRID_SIZE + 1):
        table.add_column(str(col_idx), justify='center')
    for r_idx in range(GRID_SIZE):
        cells: List[Text] = [Text(str(r_idx + 1), style='bold red')]
        for c_idx in range(GRID_SIZE):
            pos = (r_idx, c_idx)
            if pos in traps:
                cell = Text('T', style='bold red reverse')
            elif pos == ENTRY:
                cell = Text('E', style='bold green')
            elif pos == EXIT:
                cell = Text('X', style='bold magenta')
            else:
                cell = Text(grid[r_idx][c_idx], style='dim')
            cells.append(cell)
        table.add_row(*cells)
    console.print(table)
    time.sleep(2)
    print(term.clear())

    start_time = time.time()
    traps_hit = 0
    last_beep = start_time
    input_buffer: str = ''

    with term.cbreak(), term.hidden_cursor():
        while True:
            elapsed = time.time() - start_time
            remaining = TIME_LIMIT - elapsed
            if remaining <= 0 or traps_hit >= ALERT_THRESHOLD:
                glitch_effect()
                console.print(
                    Text("== OVERRIDE FAILED: TRACE LOCKDOWN ==",
                         style='bold red')
                )
                return False

            # Beep faster as timer winds down
            # Keep interval >= MIN_BEEP_INTERVAL
            frac = max(0.0, min(1.0, remaining / TIME_LIMIT))
            interval = MIN_BEEP_INTERVAL + (
                (INITIAL_BEEP_INTERVAL - MIN_BEEP_INTERVAL) * frac
            )
            if time.time() - last_beep >= interval:
                console.bell()
                last_beep = time.time()

            # Refresh display
            print(term.clear())
            draw_status(traps_hit, remaining)
            print_grid(grid)
            console.print(
                "Enter rotation [row,col] (e.g. 2,3) or 'q' to abort: "
                f"{input_buffer}",
                end=''
            )

            key = term.inkey(timeout=0.1)
            if not key:
                continue
            if key.name == 'KEY_ENTER':
                user_input = input_buffer.strip()
                input_buffer = ''
                # process submission
                if user_input.lower() == 'q':
                    console.print("\nAbort sequence initiated. Returning to menu...")
                    return False
                try:
                    r_str, c_str = (s.strip() for s in user_input.split(','))
                    sel_row = int(r_str) - 1
                    sel_col = int(c_str) - 1
                except Exception:
                    console.print("\n", Text(
                        "Invalid format. Use row,col (e.g. 2,3)",
                        style='bold red'
                    ))
                    time.sleep(1)
                    continue

                if (sel_row, sel_col) in traps:
                    traps_hit += 1
                    glitch_effect()
                    console.print(Text("Trap triggered! Nanobot lost.",
                                        style='bold red'))
                    time.sleep(1)
                    continue

                if 0 <= sel_row < GRID_SIZE and 0 <= sel_col < GRID_SIZE:
                    rotate_tile(grid, sel_row, sel_col)
                else:
                    console.print(Text("Coordinates out of range.",
                                        style='bold red'))
                    time.sleep(1)
                    continue

                # win check after rotation
                if is_solved(grid, traps):
                    console.clear()
                    console.print(Text(
                        "== OVERRIDE SUCCESS: AIR GAP BREACHED ==",
                        style='bold green'
                    ))
                    return True
            elif key.name == 'KEY_BACKSPACE':
                input_buffer = input_buffer[:-1]
            elif not key.is_sequence:
                input_buffer += key


def main() -> None:
    """Entry point for the module."""
    success = circuit_override()
    if success:
        console.print(
            Text("Nanobots succeeded! Subsystem secured.",
                 style='bold green')
        )
    else:
        console.print(
            Text("Override failed. Retreat and retry.",
                 style='bold red')
        )


if __name__ == '__main__':  # pragma: no cover
    main()
