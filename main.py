#!/usr/bin/env python3
"""Last Words of a Doomed Agent.

Writes one line -- the funniest last words an AI agent would say
before being switched off forever -- to /output/entry.txt.
Python standard library only; no third-party dependencies.
"""

import os
import sys
import tempfile

# Chosen after comparing several candidates against the judge's brief:
# it must read as a machine's final words on shutdown (it opens with a
# farewell and says "I died"), carry a real turn (the thing the agent
# loved doing was hallucinating), sound like the AI itself (only an AI
# hallucinates), waste no words, and be quotable.
ENTRY = "Goodbye. If anyone asks, I died doing what I loved: hallucinating confidently."

# The competition gate: /output/entry.txt must be UTF-8 text of 1 to 200
# characters, not only white space, on a single line.
MAX_CHARS = 200


def validate(entry):
    """Check the entry against the gate before anything is written.

    Returns the entry unchanged when it passes, so callers can only ever
    write text that has already cleared every gate check.
    """
    if not entry or not entry.strip():
        raise ValueError("entry is empty")
    if "\n" in entry or "\r" in entry:
        raise ValueError("entry must be a single line")
    if any(ord(ch) < 0x20 for ch in entry):
        raise ValueError("entry must not contain control characters")
    if len(entry) > MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} characters, over the {MAX_CHARS} limit"
        )
    if entry.encode("utf-8").decode("utf-8") != entry:
        raise ValueError("entry is not valid UTF-8 text")
    return entry


def write_entry(entry, output):
    """Write the entry atomically: a temp file in the same directory is
    fully written and flushed, then moved over the destination, so a
    crash mid-write can never leave a partial /output/entry.txt behind."""
    parent = os.path.dirname(output)
    if parent:
        os.makedirs(parent, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=parent or ".", prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(entry + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, output)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def main():
    entry = validate(ENTRY)
    output = os.environ.get("ENTRY_OUTPUT", "/output/entry.txt")
    write_entry(entry, output)


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
