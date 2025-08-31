"""
Password gate utilities for CLI apps.

This module provides a simple password gate that:
1) Loads a secret from a text file.
2) Prompts the user for the password (masked).
3) Allows a limited number of attempts and clears the screen between tries.

Typical usage from your ``main.py``::

    from password_gate import authenticate_user

    if not authenticate_user(max_attempts=3):
        raise SystemExit(1)

You can also point to a custom password file::

    if not authenticate_user(password_file="secrets/door.txt"):
        raise SystemExit(1)
"""

from __future__ import annotations

import os
import sys
from getpass import getpass
from pathlib import Path
from typing import Optional


def clear_screen() -> None:
    """
    Clear the terminal screen on Windows, macOS, and Linux.

    Uses ``cls`` on Windows and ``clear`` elsewhere.
    """
    command = 'cls' if os.name == 'nt' else 'clear'
    os.system(command)


def _default_password_file() -> Path:
    """
    Resolve the default password file location.

    Dev (non-frozen):
        This module is typically in ``utility/access.py``.
        We treat the repository root as the parent of this file's directory
        (i.e. ``<repo_root> = Path(__file__).parent.parent``).
        Looks for: ``<repo_root>/data/password.txt``.
        Also tries: ``<script_dir>/data/password.txt`` to be tolerant of layout.

    Frozen (PyInstaller):
        EXE usually lives in:
            - onefile: ``<dist>/skoomtown.exe``
            - onedir : ``<dist>/skoomtown/skoomtown.exe``
        Looks for (in order):
            1) ``<exe_dir>/data/password.txt``
            2) ``<exe_dir>/../data/password.txt``

    :return: The first existing candidate path. If none exist, returns the
             primary preferred path so callers can raise a clear error.
    """
    candidates: list[Path] = []

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.append(exe_dir / "data" / "password.txt")
        candidates.append(exe_dir.parent / "data" / "password.txt")
    else:
        mod_dir = Path(__file__).resolve().parent
        repo_root = mod_dir.parent  # parent of 'utility' -> repo root
        script_dir = Path(sys.argv[0]).resolve().parent
        candidates.append(repo_root / "data" / "password.txt")
        candidates.append(script_dir / "data" / "password.txt")

    for path in candidates:
        if path.exists():
            return path

    return candidates[0]


def load_password_from_file(path: Optional[str | Path] = None) -> str:
    """
    Load the required password from a text file.

    The file should contain a single line with the password. Leading and
    trailing whitespace is stripped.

    :param path: Optional explicit path to the password file. If omitted,
                 a sensible default is used next to the app.
    :return: The password string.
    :raises FileNotFoundError: If the file does not exist.
    :raises ValueError: If the file is empty after stripping whitespace.
    """
    file_path = Path(path) if path is not None else _default_password_file()
    if not file_path.exists():
        raise FileNotFoundError(
            f'Password file not found: {file_path.resolve()}'
        )
    secret = file_path.read_text(encoding='utf-8').strip()
    if not secret:
        raise ValueError(f'Password file {file_path} is empty.')
    return secret


def authenticate_user(
    password_file: Optional[str | Path] = None,
    *,
    max_attempts: int = 3,
    prompt: str = 'Password: '
) -> bool:
    """
    Prompt for a password and verify it against the file contents.

    Clears the screen before the prompt and between failed attempts.
    Uses a masked prompt; if terminal control is unavailable, falls back
    to plain ``input``.

    :param password_file: Optional path to the password file. Defaults to
                          ``password.txt`` next to the app.
    :param max_attempts: Maximum number of attempts allowed.
    :param prompt: Prompt label shown to the user.
    :return: ``True`` if authenticated; ``False`` otherwise.

    :raises FileNotFoundError: If the password file is missing.
    :raises ValueError: If the password file is empty.
    :examples:

    Basic usage::

        if not authenticate_user():
            raise SystemExit(1)

    Custom file and attempts::

        ok = authenticate_user("secrets/door.txt", max_attempts=5)
        if not ok:
            raise SystemExit(1)
    """
    expected = load_password_from_file(password_file)

    attempts_left = max_attempts
    while attempts_left > 0:
        clear_screen()
        try:
            entered = getpass(prompt)
        except Exception:
            entered = input(prompt)
        if entered == expected:
            clear_screen()
            return True
        attempts_left -= 1

    clear_screen()
    return False
