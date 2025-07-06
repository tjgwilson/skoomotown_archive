"""
Data Stream Decryption game module for Skoomtown Archive.

A multi-stage, fast-paced CLI hacking mini-game:
- Streams of random text scroll like a matrix cascade
- Secret packets appear; you must memorise them
- Under strict time pressure, type the packets to exfiltrate data
- Errors raise intrusion alerts; too many and you're cut off
- Track data fragments exfiltrated, throughput, and alert levels
- Later stages include decoy packets in alternate colours
- Embedded narrative and hacky prompts drive the fiction
"""

import random
import time
from typing import List, Tuple

from blessed import Terminal
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()
term = Terminal()


def generate_random_stream(length: int) -> str:
    """
    Generate a random uppercase alphanumeric string.

    :param length: Desired length of the stream.
    :return: Randomly-generated string.
    """
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(alphabet) for _ in range(length))


def _draw_header(
    stage: int,
    fragments: int,
    throughput: int,
    alert_level: int,
    alert_threshold: int,
    time_left: float
) -> None:
    """
    Render the top status panel with stage, data fragments, throughput,
    alert bar, and countdown timer.
    """
    alert_bar = '■' * alert_level + '·' * (alert_threshold - alert_level)
    header = Panel(
        Text.assemble(
            (" STG ", "bold white on black"), (f"{stage}", "bold yellow"),
            ("  FRAG ", "bold white on black"), (f"{fragments}KB ", "bold green"),
            (" THP ", "bold white on black"), (f"×{throughput} ", "bold magenta"),
            (" ALRT ", "bold white on black"), (alert_bar + " ", "bold red"),
            (" TIME ", "bold white on black"), (f"{time_left:0.1f}s", "bold cyan"),
        ),
        title=" Skoomtown Archive Intrusion ",
        border_style="white"
    )
    console.print(header)


def _scroll_stream(
    secret: str,
    decoys: List[Tuple[str, str]],
    rows: int,
    width: int,
    delay: float
) -> None:
    """
    Scroll a matrix of random text, injecting the secret packet and any decoys on random rows.

    :param secret: The code fragment to hide in the stream.
    :param decoys: List of (decoy_string, style) tuples.
    :param rows: Number of lines to display.
    :param width: Width of each line.
    :param delay: Seconds between frames.
    """
    # choose rows for secret and decoys
    secret_row = random.randrange(2, rows - 2)
    decoy_rows = random.sample([r for r in range(2, rows-2) if r != secret_row],
                              k=len(decoys))

    for row in range(rows):
        buffer = list(generate_random_stream(width))
        if row == secret_row:
            pos = random.randrange(0, width - len(secret))
            buffer[pos:pos + len(secret)] = list(secret)
            line = Text(''.join(buffer))
            line.stylize("bold reverse red", pos, pos + len(secret))
        elif row in decoy_rows:
            idx = decoy_rows.index(row)
            decoy, style = decoys[idx]
            pos = random.randrange(0, width - len(decoy))
            buffer[pos:pos + len(decoy)] = list(decoy)
            line = Text(''.join(buffer))
            line.stylize(style, pos, pos + len(decoy))
        else:
            line = Text(''.join(buffer), style="dim")
        console.print(line)
        time.sleep(delay)


def data_stream_decrypt(
    max_stages: int = 5,
    base_width: int = 40,
    base_rows: int = 12,
    base_delay: float = 0.25,
    base_time: float = 6.0,
    alert_threshold: int = 3
) -> bool:
    """
    Run the multi-stage Data Stream Decryption puzzle.

    Levels 4 and 5 include decoy packets in a different colour.
    Code length increases each stage, but time limits remain generous.

    :return: True if all stages are cleared; False on detection.
    """
    fragments = 0
    throughput = 1

    console.print("\n[italic dim]Infiltrating Skoomtown Archive mainframe...[/italic dim]\n")
    time.sleep(1.0)

    for stage in range(1, max_stages + 1):
        width = base_width + (stage - 1) * 5
        rows = base_rows + (stage - 1) * 3
        delay = max(base_delay - (stage - 1) * 0.02, 0.1)
        time_limit = base_time - (stage - 1) * 0.5
        code_len = 4 + (stage - 1)

        # prepare decoys for later stages
        decoys: List[Tuple[str, str]] = []
        if stage >= 4:
            # generate two decoys in yellow for stage 4, three for stage 5
            count = 2 if stage == 4 else 3
            decoys = [(generate_random_stream(code_len), "bold reverse yellow")
                      for _ in range(count)]

        secret = generate_random_stream(code_len)
        alert_level = 0

        # Clear and announce stage
        print(term.clear())
        console.print(f"[bold cyan]>> Stage {stage} Engaged <<[/bold cyan]\n")
        console.print(
            f"[dim]Stage protocols: decrypt {code_len}-byte packet under fire."  
            "Memorise amidst decoys." if decoys else "" + "\n"
        )

        # Display matrix with secret and decoys
        _scroll_stream(secret, decoys, rows, width, delay)

        # Input phase: blind typing
        start_time = time.time()
        last_beep = start_time
        entered = ""

        while (
            len(entered) < len(secret)
            and alert_level < alert_threshold
            and (time.time() - start_time) < time_limit
        ):
            elapsed = time.time() - start_time
            remaining = time_limit - elapsed

            # adaptive beep
            init_int, min_int = 1.0, 0.2
            interval = min_int + (init_int - min_int) * (remaining / time_limit)
            if time.time() - last_beep >= interval:
                console.bell()
                last_beep = time.time()

            # update header only
            print(term.move_xy(0, 0) + term.clear_eol(), end="")
            _draw_header(stage, fragments, throughput,
                         alert_level, alert_threshold, remaining)

            # capture keystroke silently
            key = term.inkey(timeout=0.1)
            if not key or key.is_sequence:
                continue
            char = key.upper()
            if char == secret[len(entered)]:
                entered += char
            else:
                alert_level += 1
                console.print(
                    Text("UNUSUAL ACTIVITY DETECTED!",
                         style="bold black on yellow")
                )
                time.sleep(0.3)

        success = (entered == secret) and (alert_level < alert_threshold)

        # outcome
        if success:
            elapsed = time.time() - start_time
            base_pts = stage * 150
            speed_bonus = int((time_limit - elapsed) * 15) * throughput
            gained = base_pts * throughput + max(speed_bonus, 0)
            fragments += gained
            throughput += 1

            console.print(f"\n[bold green]✔ Packet {stage} Exfiltrated![/bold green]")
            console.print(
                f"[green]+{base_pts} base +{max(speed_bonus,0)} bonus -> {gained}KB[/green]\n"
            )
            time.sleep(1.2)
        else:
            console.print("\n[bold red]== INTRUSION DETECTED: CONNECTION TERMINATED ==[/bold red]\n")
            console.print(f"[red]Packet {stage} was: {secret}[/red]\n")
            return False

    console.print("\n[bold magenta]== ARCHIVE BREACHED: ALL FRAGMENTS EXFILTRATED ==[/bold magenta]")
    console.print(f"[yellow]Total Data Exfiltrated: {fragments}KB[/yellow]\n")
    return True


if __name__ == "__main__":
    if data_stream_decrypt():
        console.print("[bold green]Mission accomplished: Data secured![/bold green]\n")
    else:
        console.print("[bold red]Mission failed: Trace nuke imminent![/bold red]\n")
