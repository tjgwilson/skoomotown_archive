import random
import time
from typing import List, Set, Tuple, Optional

from blessed import Terminal
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
term = Terminal()

# Configuration constants
GRID_SIZE: int = 5
TRAP_COUNT: int = 3
TIME_LIMIT: float = 300.0  # seconds for puzzle
ALERT_THRESHOLD: int = 1  # max traps before failure

# Glitch effect constants
GLITCH_FRAMES: int = 6
GLITCH_DELAY: float = 0.05
GLITCH_CHARS: str = '░▒▓█<>*'

# Beep intervals
INITIAL_BEEP_INTERVAL: float = 1.0  # start interval
MIN_BEEP_INTERVAL: float = 0.2      # fastest beep

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
    """
    Display a red glitch animation on detection.
    """
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
    """
    Render the top status bar: time remaining and traps triggered.
    """
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
    """
    Display the grid with row and column labels.
    """
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


def is_solved(grid: List[List[str]],
              traps: Set[Tuple[int, int]]) -> bool:
    """
    Return True if a valid path connects ENTRY to EXIT avoiding traps.

    :param grid: Current tile grid.
    :param traps: Set of trap coordinates.
    :return: Whether the puzzle is solved.
    """
    visited: Set[Tuple[int, int]] = set()
    stack: List[Tuple[int, int]] = [ENTRY]
    opposite = {'N': 'S', 'S': 'N', 'W': 'E', 'E': 'W'}

    while stack:
        row, col = stack.pop()
        if (row, col) in visited or (row, col) in traps:
            continue
        visited.add((row, col))
        if (row, col) == EXIT:
            return True
        for direction in CONNECTIONS[grid[row][col]]:
            new_row = row + (direction == 'S') - (direction == 'N')
            new_col = col + (direction == 'E') - (direction == 'W')
            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                if opposite[direction] in CONNECTIONS[grid[new_row][new_col]]:
                    stack.append((new_row, new_col))
    return False


def circuit_override() -> bool:
    """
    Execute the circuit override puzzle with continuous timer.

    Press Enter to start, rotate tiles using manual input captured per keystroke.
    :return: True on success, False on failure or abort.
    """
    # Build solution path and place traps
    solution_path: List[Tuple[int, int]] = [ENTRY]
    row, col = ENTRY
    while (row, col) != EXIT:
        if row < GRID_SIZE - 1 and (
                random.choice([True, False]) or col == GRID_SIZE - 1):
            row += 1
        else:
            col = min(col + 1, GRID_SIZE - 1)
        solution_path.append((row, col))

    traps = set(random.sample(
        [pos for pos in (
            (r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
        ) if pos not in solution_path], TRAP_COUNT
    ))

    # Initialise and scramble grid
    grid = [[random.choice(TILES) for _ in range(GRID_SIZE)]
            for _ in range(GRID_SIZE)]
    for pr, pc in solution_path:
        neighbours = {
            d for (dr, dc), d in {
                (-1, 0): 'N', (1, 0): 'S', (0, -1): 'W', (0, 1): 'E'
            }.items() if (pr + dr, pc + dc) in solution_path
        }
        for tile, conns in CONNECTIONS.items():
            if conns == neighbours:
                grid[pr][pc] = tile
                break
    for r_idx in range(GRID_SIZE):
        for c_idx in range(GRID_SIZE):
            for _ in range(random.randint(0, 3)):
                grid[r_idx][c_idx] = ROTATION_MAP[grid[r_idx][c_idx]]

    # Intro sequence
    print(term.clear())
    console.print("[bold cyan]Circuit Override Protocol Ready[/bold cyan]")
    console.print(
        "[dim]Deploy nanobots to bridge the air gap in the Skoomtown Archive vault.\n"
        "Rotate tiles to form a path from [green]E[/green] to [magenta]X[/magenta]. "
        f"Avoid {TRAP_COUNT} traps hidden by wizard encryptions. "
        "Traps will flash briefly at start—memorise their locations!\n"
        f"Time limit: {TIME_LIMIT} seconds. Press Enter to begin.[/dim]"
    )
    term.inkey()

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
            interval = (MIN_BEEP_INTERVAL +
                        (INITIAL_BEEP_INTERVAL - MIN_BEEP_INTERVAL) *
                        (remaining / TIME_LIMIT))
            if time.time() - last_beep >= interval:
                console.bell()
                last_beep = time.time()

            # Refresh display
            print(term.clear())
            draw_status(traps_hit, remaining)
            print_grid(grid)
            console.print(f"Enter rotation [row,col] (e.g. 2,3) or 'q' to abort: {input_buffer}", end='')

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
    """
    Entry point for the module.
    """
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
