# games/intro.py
import time
from blessed import Terminal
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()
term = Terminal()

def show_module_intro(title: str, description: str) -> None:
    """
    Display a standardized intro panel for every protocol.
    """
    panel = Panel(
        Text.from_markup(
            f"[bold cyan]== [bold white]{title}[/bold white] [bold cyan]==\n"
            f"{description}"
        ),
        border_style="bright_blue",
        subtitle="Press any key to continue...",
        subtitle_align="center",
        padding=(1, 2),
    )
    console.clear()
    console.print(panel)
    term.inkey()      # wait for any key
    console.clear()
    time.sleep(0.2)  # small pause before next draw
