"""
Unlocked text loader and display utilities.

These functions let you reveal a hidden text file once all sub-games
are complete. The file is displayed on a cleared screen using Rich.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional
import time

from blessed import Terminal
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

term = Terminal()
console = Console()


def _default_secret_file() -> Path:
    """
    Resolve the default unlocked-text file path.

    Prefers ``vault.txt`` alongside a frozen executable (PyInstaller).
    Otherwise uses the directory of the running script.

    :return: Path to the default secret file.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.parent / 'data' / "vault.txt"
    return Path(sys.argv[0]).resolve().parent.parent / 'data' / "vault.txt"


def load_unlocked_text(path: Optional[str | Path] = None) -> str:
    """
    Load the unlocked text from a file.

    :param path: Optional explicit path to the text file. If omitted,
                 defaults to ``vault.txt`` in the app directory.
    :return: Contents of the file as a string.
    :raises FileNotFoundError: If the file does not exist.
    """
    file_path = Path(path) if path is not None else _default_secret_file()
    text = file_path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def show_unlocked_text(path: Optional[str | Path] = None) -> None:
    """
    Clear the screen and display the unlocked text inside a panel.

    Waits for Enter before returning to the caller.

    :param path: Optional explicit path to the text file.
    """
    console.clear()
    try:
        payload = load_unlocked_text(path)
    except FileNotFoundError as exc:
        console.print(Panel(str(exc), title="File not found", style="red"))
        console.input("\nPress Enter to return…")
        return


    console.print(
        Panel(
            Text(payload, style="bold"),
            title="<< UNLOCKED ARCHIVE >>",
            border_style="cyan",
            padding=(1, 2),
            subtitle="Press enter to continue...",
        ),
    )
    term.inkey()      # wait for any key
    console.clear()
