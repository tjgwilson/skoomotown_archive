"""
Main entry point for Skoomtown Archive hacking tool.

Provides a themed database infiltration interface:
- Menu to select among three hacking modules
- Tracks which modules (games) are completed
- Reveals firewall layers as each module is cracked
- Unlocks a final data view once all modules are done
- Returns to main menu on failure until exit
"""

import sys
import time
from typing import Set, Callable

from blessed import Terminal
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from games.data_stream_decrypt import data_stream_decrypt
from games.circuit_override import circuit_override
from games.firewall_matrix_breach import firewall_breach

console = Console()
term = Terminal()

# Firewall layers ASCII art
FIREWALL_LAYERS = {
    "data_stream": (
        "[=== FIREWALL LAYER 1 ===]",
        [
            "╔══════════════════════╗",
            "║ ████  ████  ████     ║",
            "║ ████░░░░░░████       ║",
            "║ ████  ████  ████     ║",
            "╚══════════════════════╝"
        ]
    ),
    "deliver_payload": (
        "[=== FIREWALL LAYER 2 ===]",
        [
            "┌─────────────────────┐",
            "│#####################│",
            "│#...#.......#.......#│",
            "│#.#.#.#####.#.###.#.#│",
            "│#.#...#...#...#...#.#│",
            "│#####.###.#.#.###.###│",
            "│#.......#.#.#...#...#│",
            "│#.#####.#.###.#.###.#│",
            "│#.#.....#.....#.....#│",
            "│#################X###│",
            "└─────────────────────┘",
        ]
    ),
    "circuit_override": (
        "[=== FIREWALL LAYER 3 ===]",
        [
            "   ┌───┐     ┌───┐",
            " ┌─┴─┐   ┌─┴─┐",
            " │   ├──■──┤   │",
            " └───┴───┴───┘"
        ]
    )
}


def print_header(completed: Set[str]) -> None:
    """
    Display the main menu header and persistent firewall map.

    :param completed: Set of completed module keys.
    """
    console.clear()
    console.print(
        Panel(
            "Skoomtown Archive Database Infiltration",
            style="bold cyan",
            subtitle="Select a module to initiate breach"
        )
    )
    for key, (title, art) in FIREWALL_LAYERS.items():
        color = "green" if key in completed else "red"
        console.print(f"[{color}]{title}[/{color}]")
        for line in art:
            console.print(Text(line, style=color))
        console.print()


def read_data() -> None:
    """
    Display secure archive data once all modules are compromised.
    """
    console.clear()
    console.print(
        Panel(
            "<< SECURE FINANCIAL DATA DUMP >>\n"
            "Account ID: 042-7392-AC   Balance: 12,583,207 Cr\n"
            "Transaction Log: 5,120 entries\n"
            "Encryption Key: ZX-91Q-ARCHIVE-END\n",
            title="Skoomtown Archive Vault",
            style="bold blue"
        )
    )
    console.input("\nPress Enter to exit…")
    sys.exit(0)


def pass_game() -> bool:
    """
    Placeholder for modules not yet implemented.
    Always returns False.
    """
    console.print("[yellow]Module not implemented yet.[/yellow]")
    time.sleep(1)
    return False


def main() -> None:
    """
    Main loop presenting module selection menu and handling results.
    """
    completed: Set[str] = set()
    games: list[tuple[str, str, Callable[[], bool], str]] = [
        ("1", "Data Stream Decrypt", data_stream_decrypt, "data_stream"),
        ("2", "Deliver Nanobot payload", firewall_breach, "deliver_payload"),
        ("3", "Airgap Breach", circuit_override, "circuit_override"),
    ]

    while True:
        print_header(completed)
        console.print("[bold]Available Modules:[/bold]\n")
        for key, name, _, segment in games:
            status = "[green]✓[/green]" if segment in completed else "[red]✗[/red]"
            console.print(f" [bold]{key}[/bold]. {name} {status}")
        if len(completed) == len(games):
            console.print(" [bold]4[/bold]. Read Secure Data [green]Unlocked[/green]")
        console.print(" [bold]q[/bold]. Quit\n")

        choice = console.input(">> ").strip().lower()
        if choice == "q":
            console.print("Exiting infiltration tool. Stay covert.")
            sys.exit(0)

        handled = False
        for key, name, func, segment in games:
            if choice == key:
                handled = True
                console.print(Panel(f"Engaging module: [bold]{name}[/bold]", style="yellow"))
                success = func()
                if success and segment not in completed:
                    completed.add(segment)
                    console.print(
                        Panel(f"Node {name} compromised!", style="green")
                    )
                elif not success:
                    console.print(
                        Panel(
                            "Intrusion detected! Returning to main menu...",
                            style="red"
                        )
                    )
                time.sleep(2)
                break
        if not handled:
            if choice == "4" and len(completed) == len(games):
                read_data()
            else:
                console.print("[red]Invalid choice. Use 1,2,3,4 or q.[/red]")
                time.sleep(1)


if __name__ == "__main__":
    main()
