from __future__ import annotations
from typing import TextIO, Optional, List
import sys


class Display:
    """
    Centralized display/printing facility.

    - By default, uses Python's print() without binding to a fixed stream so
      it cooperates with contextlib.redirect_stdout/stderr used in tests.
    - Streams can be overridden for custom capture or UI integration.
    """

    def __init__(self, out: TextIO | None = None, err: TextIO | None = None):
        # If None, we will call print() without an explicit file to respect
        # active redirections (e.g., contextlib.redirect_stdout).
        self._out: Optional[TextIO] = out
        self._err: Optional[TextIO] = err

    def set_streams(self, out: Optional[TextIO] = None, err: Optional[TextIO] = None):
        if out is not None:
            self._out = out
        if err is not None:
            self._err = err

    # Primary API
    def write(self, msg: str = ""):
        if self._out is None:
            print(msg)
        else:
            print(msg, file=self._out)

    def error(self, msg: str = ""):
        if self._err is None:
            # Default to stderr dynamically
            print(msg, file=sys.stderr)
        else:
            print(msg, file=self._err)

    def lines(self, lines: List[str]):
        for line in lines:
            self.write(line)


# Export a default singleton instance for simple usage
display = Display()
