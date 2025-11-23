import contextlib
import io


def run_cmd(game, line: str) -> list[str]:
    """
    Execute a command line via the public Game.parse_and_execute and
    capture printed output. Returns a list of output lines.

    This helper intentionally avoids using any legacy helpers in
    commands.engine to keep tests independent of legacy code.
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            game.parse_and_execute(line)
        except Exception as e:
            # Surface exceptions as text to keep existing tests expectations
            print(f"Error: {e}")
    text = buf.getvalue()
    return [ln.rstrip("\r") for ln in text.splitlines()]
