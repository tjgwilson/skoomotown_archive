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

    Dev (non-frozen):
        utility/open_file.py  -> repo root at parent of this file's parent
        Looks for: <repo_root>/data/vault.txt

    Frozen (PyInstaller):
        EXE in: <dist>/skoomtown.exe  (onefile)
                or <dist>/skoomtown/skoomtown.exe (onedir)
        Looks for (in order):
            1) <exe_dir>/data/vault.txt
            2) <exe_dir>/../data/vault.txt

    :return: Path to the resolved vault file (first match), or the preferred
             path (<exe_dir>/data/vault.txt or <repo_root>/data/vault.txt)
             if none exist (so callers can show a helpful error).
    """
    candidates: list[Path] = []

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent.parent
        candidates.append(exe_dir / "data" / "vault.txt")
        candidates.append(exe_dir.parent / "data" / "vault.txt")
    else:
        # This module likely lives in utility/open_file.py
        mod_dir = Path(__file__).resolve().parent.parent
        repo_root = mod_dir.parent  # one up from 'utility' -> repo root
        # Also try based on the running script path, in case layout differs
        script_root = Path(sys.argv[0]).resolve().parent.parent
        candidates.append(repo_root / "data" / "vault.txt")
        candidates.append(script_root / "data" / "vault.txt")

    for p in candidates:
        if p.exists():
            return p

    # Fall back to the first preferred path (so you can report a clear error)
    return candidates[0]



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
