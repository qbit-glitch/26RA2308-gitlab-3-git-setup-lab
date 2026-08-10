"""Reads what a student pastes from `git config --list` and `git config --list --show-origin`.

A line is `key=value`, or `file:<path><blank>key=value` with --show-origin (the blank is a tab, or spaces after a copy
from a terminal; a Windows path may hold spaces). Every line is cut to MAX_LINE characters first.
"""
from __future__ import annotations

import re
from typing import List, NamedTuple, Optional

MAX_LINE = 500
KEY = r"([A-Za-z][^=\s]*\.[^=\s]+)"
PLAIN_RE = re.compile(rf"^{KEY}=(.*)$")
FILE_RE = re.compile(rf"^file:(.*?)\s+{KEY}=(.*)$")
NAMED_RE = re.compile(rf"^(command line:|standard input:)\s+{KEY}=(.*)$")
BLOB_RE = re.compile(rf"^(blob:\S+)\s+{KEY}=(.*)$")


class Entry(NamedTuple):
    """One setting of the listing."""

    origin: Optional[str]  # the file, or None when the listing has no origins
    key: str               # lower case
    value: str


def parse(text: str) -> List[Entry]:
    """The settings in 'text' in order. Prompts, prose and pager marks are not settings."""
    entries: List[Entry] = []
    for raw in text.split("\n"):
        line = raw[:MAX_LINE].strip()
        for pattern in (FILE_RE, NAMED_RE, BLOB_RE):
            match = pattern.match(line)
            if match:
                entries.append(Entry(match.group(1), match.group(2).lower(), match.group(3)))
                break
        else:
            match = PLAIN_RE.match(line)
            if match:
                entries.append(Entry(None, match.group(1).lower(), match.group(2)))
    return entries


def count(text: str) -> int:
    """How many settings the listing holds."""
    return len(parse(text))


def last(entries: List[Entry], key: str) -> Optional[str]:
    """The value of the last line with this key (compared in lower case), or None."""
    found = [e.value for e in entries if e.key == key.lower()]
    return found[-1] if found else None


def origin_of(entries: List[Entry], key: str) -> Optional[str]:
    """The file the last line with this key comes from, or None."""
    found = [e.origin for e in entries if e.key == key.lower()]
    return found[-1] if found else None
