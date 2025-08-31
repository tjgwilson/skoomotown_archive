import sys
import time
from typing import Callable, Set, Tuple, List

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from blessed import Terminal

from games.data_stream_decrypt import data_stream_decrypt
from games.circuit_override import circuit_override
from games.firewall_matrix_breach import firewall_breach

from utility.access import authenticate_user
from utility.open_file import show_unlocked_text

console = Console()
term = Terminal()

# Type alias for game specs: (menu key, title, callable, completion key)
GameSpec = Tuple[str, str, Callable[[], bool], str]


def show_banner() -> None:
    """
    Display the initial banner and flavour text for the tool.

    The banner is shown once at start-up before the main loop begins.
    """
    console.clear()
    console.print(
        Panel(
            Text('SKOOMTOWN ARCHIVE', style='bold magenta', justify='center'),
            border_style='magenta',
            padding=(1, 4),
        )
    )
    console.print(
        Panel(
            Text(
                'Welcome, Operative. You are accessing the Skoomtown Archive '
                'Breach Utility.\nSelect your protocol to initiate breach:\n',
                style='italic cyan',
                justify='center',
            ),
            border_style='dim white',
            subtitle="Press enter to continue...",
        )
    )


# Firewall layers ASCII art
FIREWALL_LAYERS = {
    'data_stream': (
        '[=== FIREWALL LAYER 1 ===]',
        [
            '╔══════════════════════╗',
            '║ ████  ████  ████     ║',
            '║ ████░░░░░░████       ║',
            '║ ████  ████  ████     ║',
            '╚══════════════════════╝',
        ],
    ),
    'deliver_payload': (
        '[=== FIREWALL LAYER 2 ===]',
        [
            '┌─────────────────────┐',
            '│#####################│',
            '│#...#.......#.......#│',
            '│#.#.#.#####.#.###.#.#│',
            '│#.#...#...#...#...#.#│',
            '│#####.###.#.#.###.###│',
            '│#.......#.#.#...#...#│',
            '│#.#####.#.###.#.###.#│',
            '│#.#.....#.....#.....#│',
            '│#################X###│',
            '└─────────────────────┘',
        ],
    ),
    'circuit_override': (
        '[=== FIREWALL LAYER 3 ===]',
        [
            '   ┌───┐     ┌───┐',
            ' ┌─┴─┐   ┌─┴─┐',
            ' │   ├──■──┤   │',
            ' └───┴───┴───┘',
        ],
    ),
}


def print_header(completed: Set[str]) -> None:
    """
    Display the main menu header and persistent firewall map.

    :param completed: Set of completed module keys.
    """
    console.clear()
    console.print(
        Panel(
            'Skoomtown Archive Database Infiltration',
            style='bold cyan',
            subtitle='Select a module to initiate breach',
        )
    )
    for key, (title, art) in FIREWALL_LAYERS.items():
        colour = 'green' if key in completed else 'red'
        console.print(f'[{colour}]{title}[/{colour}]')
        for line in art:
            console.print(Text(line, style=colour))
        console.print()


def main() -> None:
    """
    Run the main loop presenting the module selection menu.

    The loop renders the firewall status map, lists modules, executes the
    chosen mini-game, tracks completion state, and unlocks the final data
    readout when all modules are complete.

    :return: None
    """

    if not authenticate_user(max_attempts=3):
        print('Access denied.')
        raise SystemExit(1)

    completed: Set[str] = set()
    console.clear()
    show_banner()
    term.inkey()      # wait for any key
    console.clear()
    time.sleep(0.2)  # small pause before next draw

    games: List[GameSpec] = [
        ('1', 'Data Stream Decryption', data_stream_decrypt, 'data_stream'),
        ('2', 'Nanobot Infiltration', firewall_breach, 'deliver_payload'),
        ('3', 'Airgap Override', circuit_override, 'circuit_override'),
    ]

    while True:
        print_header(completed)
        console.print('[bold]Available Modules:[/bold]\n')
        for key, title, func, segment in games:
            status = '[green]✓[/green]' if segment in completed else '[red]✗[/red]'
            console.print(f' [bold]{key}[/bold]. {title} {status}')

        # For testing you're forcing it visible; that's fine:
        console.print(' [bold]4[/bold]. Read Secure Data [green]Unlocked[/green]')
        console.print(' [bold]q[/bold]. Quit\n')

        choice = console.input('>> ').strip().lower()
        if choice == 'q':
            console.print('Exiting infiltration tool.')
            sys.exit(0)

        handled = False  # <-- start False

        for key, title, func, segment in games:
            if choice == key:
                handled = True  # <-- set True only when we handle a game
                console.print(Panel(f'Engaging {title}', style='yellow'))
                time.sleep(0.8)

                console.clear()  # Clear before launching a sub-game

                success = func()
                if success and segment not in completed:
                    completed.add(segment)
                    console.print(Panel(f'{title} compromised!', style='green'))
                elif not success:
                    console.print(
                        Panel(
                            'Intrusion detected! Returning to main menu...',
                            style='red',
                        )
                    )
                    time.sleep(1.2)
                time.sleep(0.6)
                break

        if not handled:
            # While testing, allow 4 unconditionally. Later, re-enable the completion check.
            if choice == '4':  # and len(completed) == len(games):
                show_unlocked_text()  # loads vault.txt by default
                # After returning, loop will redraw the menu
            else:
                console.print('[red]Invalid choice. Use 1,2,3,4 or q.[/red]')
                time.sleep(0.6)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print('\n[red]Interrupted. Exiting.[/red]')
        sys.exit(0)
