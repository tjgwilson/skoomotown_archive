import time
from collections import deque
from typing import Dict, List, Optional, Tuple

from blessed import Terminal
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# --- Configuration Constants ---
# Map legend:
#  '#' = Wall
#  '.' = Open path
#  'X' = Exit point
MAZE_MAP = [
    "##################################",
    "#.....#.......##.......#.........#",
    "#.###.#.#####.##.###.#.#.###.###.#",
    "#.#...#.#...#.##...#.#.#...#...#.#",
    "#.#.###.#.#.#.#####.#.#####.#.#.##",
    "#.#.....#.#.#.....#.#.......#.#.##",
    "#.#.#####.#.#####...#########.#.##",
    "#.#.....#.#.....#.#.#.......#.#.##",
    "#.#.###.#.#####.#.#.#.#####.#.#.##",
    "#.#...#.#...#...#.#.#.#...#.#...##",
    "#.###.#.###.#####.#.#.#.#.#.######",
    "#.....#...........#...#.#.......##",
    "#####.###############.#.###.###.##",
    "#.........#.........#.#.......#.##",
    "#.#.#######.#######.#.#######.#.##",
    "#.#.........#.....#.#.........#X##",
    "##################################",
]
LASER_BEAMS = [
    {"orient": "h", "row": 2,  "cols": list(range(6, 28)), "dir":  1},
    {"orient": "h", "row": 10, "cols": list(range(2, 18)), "dir": -1},
    {"orient": "v", "col": 14, "rows": list(range(3, 12)), "dir":  1},
    {"orient": "v", "col": 24, "rows": list(range(5, 15)), "dir": -1},
]
PLAYER_ICON     = "@"
EXIT_ICON       = "X"
ALERT_THRESHOLD = 3
TIME_LIMIT      = 45.0   # seconds
REFRESH_DELAY   = 0.1    # seconds

console = Console()
term    = Terminal()


def show_intro() -> None:
    """
    Display the mission briefing and pause for operator input.
    """
    panel = Panel(
        Text.from_markup(
            """
            [bold cyan]== [bold white]SYS-BREACH PROTOCOL V4.0[/bold white] [bold cyan]==
            [bold green]Mission Briefing:[/bold green]
            - Navigate widened corridors avoiding horizontal (═) and vertical (║) laser beams.
            - Each beam hit increments ALERT; max allowed is 3.
            - Reach exit marker [bold green]X[/bold green] within 45 seconds.
            """
        ),
        subtitle="Press any key to continue...",
        subtitle_align="center",
        border_style='bright_blue',
    )
    console.clear()
    console.print(panel)
    # Wait for any key
    term.inkey()
    console.clear()
    console.print(panel)
    # Wait for any key
    term.inkey()
    console.clear()
def find_route() -> Optional[List[Tuple[int, int]]]:
    """
    Find a path from start (1,1) to exit 'X' using BFS.

    :return: List of (row, col) steps or None if unreachable.
    """
    rows, cols = len(MAZE_MAP), len(MAZE_MAP[0])
    start = (1, 1)
    end: Tuple[int, int] = (0, 0)
    for r in range(rows):
        for c in range(cols):
            if MAZE_MAP[r][c] == EXIT_ICON:
                end = (r, c)
                break
    visited = [[False] * cols for _ in range(rows)]
    prev: Dict[Tuple[int, int], Tuple[int, int]] = {}
    queue = deque([start])
    visited[start[0]][start[1]] = True

    while queue:
        r, c = queue.popleft()
        if (r, c) == end:
            break
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if not visited[nr][nc] and MAZE_MAP[nr][nc] != '#':
                    visited[nr][nc] = True
                    prev[(nr, nc)] = (r, c)
                    queue.append((nr, nc))
    if not visited[end[0]][end[1]]:
        return None

    # Reconstruct path
    path: List[Tuple[int, int]] = []
    cur = end
    while cur != start:
        path.append(cur)
        cur = prev[cur]
    path.append(start)
    path.reverse()
    return path


def flash_route(path: List[Tuple[int, int]]) -> None:
    """
    Briefly display the correct path on the map before gameplay.

    :param path: List of (row, col) coordinates for the route.
    """
    grid = [list(row) for row in MAZE_MAP]
    for r, c in path:
        if grid[r][c] == '.':
            grid[r][c] = '*'
    console.clear()
    console.print(Panel(Text("Displaying optimal route..."), border_style='magenta'))
    for row in grid:
        line = Text()
        for ch in row:
            style = {
                '#': 'grey37',
                PLAYER_ICON: 'bold yellow',
                EXIT_ICON: 'bold green',
                '*': 'bold magenta',
            }.get(ch, 'white')
            line.append(ch, style=style)
        console.print(line)
    # Briefly pause to allow user to view route
    time.sleep(3)
    console.clear()


def draw_header(alert: int, remaining: float) -> None:
    """
    Render the alert bar and countdown timer.
    """
    bar = Text('ALERT ', style='bold white')
    bar.append('■' * alert, style='bold red')
    bar.append('·' * (ALERT_THRESHOLD - alert), style='dim red')
    timer = Text(f' TIME {remaining:0.0f}s', style='bold cyan')
    console.print(Panel(bar + timer, title=' Firewall Matrix Breach ', border_style='white'))


def render_maze(player: List[int], beams: List[Dict]) -> None:
    """
    Draw maze, dynamic beams, player, and exit.
    """
    grid = [list(row) for row in MAZE_MAP]
    for b in beams:
        if b['orient'] == 'h':
            grid[b['row']][b['beam_pos']] = '═'
        else:
            grid[b['beam_pos']][b['col']] = '║'
    pr, pc = player
    grid[pr][pc] = PLAYER_ICON
    for row in grid:
        line = Text()
        for ch in row:
            style = {
                '#': 'grey37', PLAYER_ICON: 'bold yellow', EXIT_ICON: 'bold green',
                '═': 'bright_red', '║': 'bright_red'
            }.get(ch, 'white')
            line.append(ch, style=style)
        console.print(line)


def update_beams(beams: List[Dict]) -> None:
    """
    Advance beam positions with bounce logic.
    """
    for b in beams:
        key = 'cols' if b['orient'] == 'h' else 'rows'
        positions = b[key]
        idx = positions.index(b['beam_pos'])
        nxt = idx + b['dir']
        if nxt < 0 or nxt >= len(positions):
            b['dir'] *= -1
            nxt = idx + b['dir']
        b['beam_pos'] = positions[nxt]


def firewall_breach() -> bool:
    """
    Main breach routine invoked by menu: shows intro, flashes optimal route, then runs the core loop.

    :return: True on successful breach, False on failure.
    """
    # Show briefing and optimal path
    show_intro()
    path = find_route()
    if path:
        flash_route(path)

    # Initialize player, alert counter, and beams
    player = [1, 1]
    alert = 0
    beams: List[Dict] = []
    for spec in LASER_BEAMS:
        b = spec.copy()
        key = 'cols' if b['orient'] == 'h' else 'rows'
        b['beam_pos'] = b[key][0]
        beams.append(b)

    # Start timer
    start = time.time()

    with term.cbreak(), term.hidden_cursor():
        while True:
            elapsed = time.time() - start
            remaining = TIME_LIMIT - elapsed
            if remaining <= 0 or alert >= ALERT_THRESHOLD:
                return False

            console.clear()
            draw_header(alert, remaining)
            render_maze(player, beams)

            key = term.inkey(timeout=REFRESH_DELAY)
            if key.name == 'KEY_ESCAPE':
                return False

            moves = {
                'KEY_LEFT': (0, -1), 'KEY_RIGHT': (0, 1),
                'KEY_UP': (-1, 0), 'KEY_DOWN': (1, 0)
            }
            dr, dc = moves.get(key.name, (0, 0))

            nr, nc = player[0] + dr, player[1] + dc
            if MAZE_MAP[nr][nc] != '#':
                player = [nr, nc]

            # Check collisions with beams
            for b in beams:
                if b['orient'] == 'h' and b['row'] == player[0] and b['beam_pos'] == player[1]:
                    alert += 1
                if b['orient'] == 'v' and b['col'] == player[1] and b['beam_pos'] == player[0]:
                    alert += 1

            # Check for exit
            if MAZE_MAP[player[0]][player[1]] == EXIT_ICON:
                return True

            update_beams(beams)

    # unreachable

def main() -> None:
    """
    Run intro, flash optimal route, then execute breach.
    """
    show_intro()
    path = find_route()
    if path:
        flash_route(path)
    result = firewall_breach()
    console.clear()
    if result:
        console.print('[bold green]>> PAYLOAD DELIVERED: CORE COMPROMISED <<[/bold green]')
    else:
        console.print('[bold red]>> IDS OVERRIDE: ACCESS DENIED <<[/bold red]')

if __name__ == '__main__':
    main()
