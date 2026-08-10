"""Reads a git configuration file (~/.gitconfig, .git/config) as text, the way git reads it, for the keys the lab grades.

It never runs git and never follows an `include`. Everything is bounded in line count and line length, so a hostile or
huge file cannot make the grader slow. test_gitconfig.py checks the reading against `git config --file --list`.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

MAX_LINES = 20000
MAX_LINE = 4096
KEY_RE = re.compile(r"[A-Za-z][A-Za-z0-9-]*")
SECTION_RE = re.compile(r'\[\s*([A-Za-z0-9.-]+)(?:\s+"((?:[^"\\]|\\.)*)")?\s*\]')
ESCAPES = {"n": "\n", "t": "\t", "b": "\b", "\\": "\\", '"': '"'}


def _logical_lines(text: str) -> List[str]:
    """The lines of the file, with a line that ends in a backslash joined to the next one."""
    physical = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")[:MAX_LINES]
    logical: List[str] = []
    pending = ""
    for raw in physical:
        line = raw[:MAX_LINE]
        trailing = len(line) - len(line.rstrip("\\"))
        if trailing % 2 == 1:
            pending += line[:-1]
            continue
        logical.append(pending + line)
        pending = ""
    if pending:
        logical.append(pending)
    return logical


def _value(rest: str) -> str:
    """The value after '=': quotes group, backslash escapes, # or ; outside quotes ends it, outer blanks go."""
    chars: List[Tuple[str, bool]] = []  # (character, kept even if it is a blank at the edge)
    quoted = escaped = False
    for ch in rest:
        if escaped:
            chars.append((ESCAPES.get(ch, ch), True))
            escaped = False
        elif ch == "\\":
            escaped = True
        elif ch == '"':
            quoted = not quoted
        elif not quoted and ch in "#;":
            break
        else:
            chars.append((ch, quoted))
    while chars and chars[0][0] in " \t" and not chars[0][1]:
        chars.pop(0)
    while chars and chars[-1][0] in " \t" and not chars[-1][1]:
        chars.pop()
    return "".join(ch for ch, _ in chars)


def _section_prefix(name: str, sub: Optional[str]) -> str:
    if sub is not None:
        unescaped = re.sub(r"\\(.)", r"\1", sub)  # \" and \\ in a subsection name stand for " and \
        return f"{name.lower()}.{unescaped}."
    if "." in name:  # the old form [section.subsection]: the subsection is compared in lower case
        head, _, tail = name.partition(".")
        return f"{head.lower()}.{tail.lower()}."
    return name.lower() + "."


def parse(text: str) -> List[Tuple[str, Optional[str]]]:
    """(key, value) of every setting in order; the value is None for a key without '='. Keys are lower case, in
    git's own spelling `section.subsection.name`."""
    entries: List[Tuple[str, Optional[str]]] = []
    prefix = ""
    for line in _logical_lines(text.lstrip("\ufeff")):  # git skips a byte order mark at the start of the file
        pos = len(line) - len(line.lstrip(" \t"))
        while pos < len(line):
            ch = line[pos]
            if ch in "#;":
                break
            if ch == "[":
                match = SECTION_RE.match(line, pos)
                if not match:
                    break
                prefix = _section_prefix(match.group(1), match.group(2))
                pos = match.end()
                pos += len(line[pos:]) - len(line[pos:].lstrip(" \t"))
                continue
            key = KEY_RE.match(line, pos)
            if not key or not prefix:
                break
            pos = key.end()
            pos += len(line[pos:]) - len(line[pos:].lstrip(" \t"))
            if pos < len(line) and line[pos] == "=":
                entries.append((prefix + key.group(0).lower(), _value(line[pos + 1:])))
            else:
                entries.append((prefix + key.group(0).lower(), None))
            break
    return entries


def values(text: str) -> Dict[str, List[str]]:
    """Every value of every key, in file order (a key without a value counts as an empty one)."""
    found: Dict[str, List[str]] = {}
    for key, value in parse(text):
        found.setdefault(key, []).append(value or "")
    return found


def last(text: str, key: str) -> Optional[str]:
    """The value git would give for 'key' (the last one), or None."""
    found = values(text).get(key.lower())
    return found[-1] if found else None
