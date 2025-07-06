"""
Main entry point for Skoomtown Archive hacking tool.

Provides a themed database infiltration interface:
- Menu to select among three hacking modules
- Tracks which modules (games) are completed
- Reveals firewall layers as each module is cracked
- Returns to main menu on failure
- Displays full network topology when all layers are breached
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
    "circuit_override": (
        "[=== FIREWALL LAYER 3 ===]",
        [
            "   ┌───┐     ┌───┐",
            " ┌─┴─┐   ┌─┴─┐",
            " │   ├──■──┤   │",
            " └───┴───┴───┘"
        ]
    ),
    "password_matrix": (
        "[=== FIREWALL LAYER 2 ===]",
        [
            "┌──────────────────────┐",
            "│ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   │",
            "│ ▒░░▒░░▒░░▒░░▒░░▒░░▒  │",
            "│ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   │",
            "└──────────────────────┘"
        ]
    )
}


def print_header(completed: Set[str]) -> None:
    """
    Display the main menu header and persistent firewall map.

    :param completed: Set of completed module keys.
    """
    console.clear()
    # Title panel
    console.print(
        Panel(
            "Skoomtown Archive Database Infiltration",
            style="bold cyan",
            subtitle="Select a module to initiate breach"
        )
    )
    # Display firewall map, coloring completed layers green
    for key, (title, art) in FIREWALL_LAYERS.items():
        color = "green" if key in completed else "red"
        console.print(f"[{color}]{title}[/{color}]")
        for line in art:
            console.print(Text(line, style=color))
        console.print()


def pass_game() -> bool:
    """
    Placeholder for future game modules.
    Always returns False for now.
    """
    console.print("[yellow]Module not yet implemented.[/yellow]")
    time.sleep(1)
    return False


def main() -> None:
    """
    Main loop presenting module selection menu and handling result.
    """
    completed: Set[str] = set()
    games: list[tuple[str, str, Callable[[], bool], str]] = [
        ("1", "Data Stream Decrypt", data_stream_decrypt, "data_stream"),
        ("2", "Password Matrix", circuit_override, "circuit_override"),
        ("3", "Circuit Override", pass_game, "circuit_override"),
    ]

    while True:
        print_header(completed)
        console.print("[bold]Available Modules:[/bold]\n")
        for key, name, _, segment in games:
            status = "[green]✓[/green]" if segment in completed else "[red]✗[/red]"
            console.print(f" [bold]{key}[/bold]. {name} {status}")
        console.print(" [bold]q[/bold]. Quit\n")

        choice = console.input(">> ").strip().lower()
        if choice == "q":
            console.print("Exiting infiltration tool. Stay covert.")
            sys.exit(0)

        for key, name, func, segment in games:
            if choice == key:
                console.print(Panel(f"Engaging module: [bold]{name}[/bold]", style="yellow"))
                success = func()
                if success:
                    if segment not in completed:
                        completed.add(segment)
                        console.print(
                            Panel(
                                f"Access granted to node {name}!",
                                title="Node Compromised",
                                style="green"
                            )
                        )
                    else:
                        console.print("[blue]Module already compromised. Move on.[/blue]")
                else:
                    console.print(
                        Panel(
                            "Intrusion detected! Returning to main menu...",
                            style="red"
                        )
                    )
                time.sleep(2)
                break
        else:
            console.print("[red]Invalid selection. Choose 1, 2, 3 or q.[/red]")
            time.sleep(1)

        if len(completed) == len(games):
            print_header(completed)
            console.print(
                Panel(
                    "All firewall layers breached! Full network topology revealed.",
                    style="magenta"
                )
            )
            console.print("[bold green]Mission complete: Financial archives exfiltrated![/bold green]")
            break


if __name__ == "__main__":
    main()
