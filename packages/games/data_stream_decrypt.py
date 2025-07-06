import random
import time
from typing import List, Tuple

from blessed import Terminal
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Constants for easy tuning
MAX_STAGES = 5
BASE_WIDTH = 40
BASE_ROWS = 12
BASE_DELAY = 0.25        # seconds between matrix frames
BASE_TIME = 12.0         # initial time limit for input phase
TIME_DECREMENT = 0.5     # seconds reduced per stage
DELAY_DECREMENT = 0.02   # seconds reduced per stage for scroll speed
MIN_DELAY = 0.1
ALERT_THRESHOLD = 3
DECOY_STYLE = "bold reverse yellow"
INITIAL_BEEP_INTERVAL = 1.0  # seconds
MIN_BEEP_INTERVAL = 0.2      # seconds
GLITCH_FRAMES = 6
GLITCH_DELAY = 0.05
GLITCH_CHARS = '░▒▓█<>*'

console = Console()
term = Terminal()


def generate_random_stream(length: int) -> str:
    """
    Generate a random uppercase alphanumeric string.
    """
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(alphabet) for _ in range(length))


def glitch_effect(frames: int = GLITCH_FRAMES, delay: float = GLITCH_DELAY) -> None:
    """
    Simulate a screen glitch effect upon intrusion detection.
    """
    width = term.width or BASE_WIDTH
    height = (term.height or (BASE_ROWS * 2)) // 4
    for _ in range(frames):
        print(term.clear())
        for _ in range(height):
            line = ''.join(random.choice(GLITCH_CHARS) for _ in range(width))
            console.print(Text(line, style="bold red"))
        time.sleep(delay)
    print(term.clear())


def _draw_header(
    stage: int,
    fragments: int,
    throughput: int,
    alert_level: int,
    time_left: float
) -> None:
    """
    Render status panel with stage, fragments, throughput, alerts, and timer.
    """
    alert_bar = '■' * alert_level + '·' * (ALERT_THRESHOLD - alert_level)
    header = Panel(
        Text.assemble(
            (" STG ", "bold white on black"), (f"{stage}", "bold yellow"),
            (" FRAG ", "bold white on black"), (f"{fragments}KB", "bold green"),
            (" THP ", "bold white on black"), (f"×{throughput}", "bold magenta"),
            (" ALRT ", "bold white on black"), (alert_bar, "bold red"),
            (" TIME ", "bold white on black"), (f"{time_left:0.1f}s", "bold cyan"),
        ),
        title=" Skoomtown Archive Intrusion ", border_style="white"
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
    Scroll matrix of text injecting secret and decoys.
    """
    secret_row = random.randrange(2, rows - 2)
    decoy_rows = random.sample(
        [r for r in range(2, rows - 2) if r != secret_row], k=len(decoys)
    )
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


def data_stream_decrypt() -> bool:
    """
    Run the multi-stage Data Stream Decryption puzzle.
    """
    fragments = 0
    throughput = 1

    console.print("\n[italic dim]Infiltrating Skoomtown Archive mainframe...[/italic dim]\n")
    time.sleep(1.0)

    # Put terminal into cbreak for per-keystroke input and hide cursor
    with term.cbreak(), term.hidden_cursor():
        for stage in range(1, MAX_STAGES + 1):
            width = BASE_WIDTH + (stage - 1) * 5
            rows = BASE_ROWS + (stage - 1) * 3
            delay = max(BASE_DELAY - (stage - 1) * DELAY_DECREMENT, MIN_DELAY)
            time_limit = max(BASE_TIME - (stage - 1) * TIME_DECREMENT, BASE_TIME / 2)
            code_len = 4 + (stage - 1)

            # Stage intro
            print(term.clear())
            console.print(f"[bold cyan]>> Stage {stage} Protocol Initiated <<[/bold cyan]")
            console.print(
                "[dim]Vault target: Skoomtown Archive core.\n"
                "Wizard-grade encryptions guard the data.\n"
                "Find the packet among decoys, then type it before being detected.[/dim]\n"
            )
            console.print("Press [bold]Enter[/bold] to deploy hack sequence...")
            term.inkey()

            # Drain any leftover input before starting
            while term.inkey(timeout=0.1):
                pass

            # Prepare decoys and secret
            decoys: List[Tuple[str, str]] = []
            if stage >= 4:
                count = 2 if stage == 4 else 3
                decoys = [(generate_random_stream(code_len), DECOY_STYLE) for _ in range(count)]
            secret = generate_random_stream(code_len)
            alert_level = 0

            # Scroll the matrix
            _scroll_stream(secret, decoys, rows, width, delay)

            # Input loop: per-letter check
            start = time.time()
            last_beep = start
            entered = ""

            while (
                len(entered) < len(secret)
                and alert_level < ALERT_THRESHOLD
                and (time.time() - start) < time_limit
            ):
                remaining = time_limit - (time.time() - start)
                # beep timing
                interval = MIN_BEEP_INTERVAL + (
                    INITIAL_BEEP_INTERVAL - MIN_BEEP_INTERVAL
                ) * (remaining / time_limit)
                if time.time() - last_beep >= interval:
                    console.bell()
                    last_beep = time.time()

                # refresh header
                print(term.move_xy(0, 0) + term.clear_eol(), end="")
                _draw_header(stage, fragments, throughput, alert_level, remaining)

                # capture and evaluate keystroke
                key = term.inkey(timeout=0.1)
                if not key or key.is_sequence:
                    continue
                char = key.upper()
                if char == secret[len(entered)]:
                    entered += char
                else:
                    alert_level += 1
                    console.print(
                        Text("UNUSUAL ACTIVITY DETECTED!", style="bold black on yellow")
                    )
                    time.sleep(0.2)

            success = (entered == secret) and (alert_level < ALERT_THRESHOLD)
            if not success:
                # glitch and failure messaging
                glitch_effect()
                console.print(
                    "[bold red]== INTRUSION DETECTED: CONNECTION TERMINATED ==[/bold red]\n"
                )
                console.print(f"[red]Expected packet: {secret}[/red]\n")

                # drain leftover keys before exit
                while term.inkey(timeout=0.1):
                    pass
                return False

            # success outcome
            elapsed = time.time() - start
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

            # drain before next stage
            while term.inkey(timeout=0.1):
                pass

    # All stages complete
    console.print(
        "\n[bold magenta]== ARCHIVE BREACHED: ALL FRAGMENTS EXFILTRATED ==[/bold magenta]"
    )
    console.print(f"[yellow]Total Data Exfiltrated: {fragments}KB[/yellow]\n")
    return True


if __name__ == "__main__":
    if data_stream_decrypt():
        console.print("[bold green]Mission accomplished: Data secured![/bold green]\n")
    else:
        console.print("[bold red]Mission failed: Trace nuke imminent![/bold red]\n")
