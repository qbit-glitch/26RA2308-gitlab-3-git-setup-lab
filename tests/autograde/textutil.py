"""Helpers for reading the text a student pasted into submission/outputs.txt."""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Sequence, Tuple

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
BOUNDARY_RE = re.compile(r"^(?:---\s*(\d+\.\d+)\b.*|===\s*TASK\b.*)$", re.MULTILINE)
PLACEHOLDER = "(paste output here)"
QUESTION_RE = re.compile(r"^(?:# Q\d+ |ANSWER-\d+\s*:)")  # the question and answer lines that sit between steps
HEADER_RE = re.compile(r"^---\s*(\d+\.\d+)\s+(.*?)\s*---\s*$")
THEN = "   then   "
MAX_LINE = 500
PLACEHOLDERS = ("Your Full Name", "your-email@your-college.edu")  # what the template header shows for the name and the email
PROMPT_SIGNS = "$%>#\u276f\u279c\u00bb"  # the signs a prompt ends in, starship and oh-my-zsh arrows included


def normalise(text: str) -> str:
    """Remove colour codes and carriage returns and strip trailing blanks."""
    text = ANSI_RE.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n"))


def parse_steps(text: str) -> Dict[str, str]:
    """Split the submission into {step id: pasted text}, e.g. {"2.3": "..."}."""
    steps: Dict[str, str] = {}
    matches = list(BOUNDARY_RE.finditer(text))
    for index, match in enumerate(matches):
        step_id = match.group(1)
        if step_id is None:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end]
        kept = [line for line in body.split("\n") if line.strip() != PLACEHOLDER and not QUESTION_RE.match(line)]
        body = "\n".join(kept).strip("\n")
        steps[step_id] = (steps[step_id] + "\n" + body) if step_id in steps else body
    return steps


def header_field(text: str, label: str) -> str:
    """Return the value of a 'Label : value' line near the top of the file."""
    match = re.search(rf"^{label}\s*:[ \t]*(.*)$", text, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def get_answer(text: str, number: int) -> str:
    """Return the student's ANSWER-<number> value ('' if blank or a placeholder)."""
    match = re.search(rf"^ANSWER-{number}[ \t]*:[ \t]*(.*)$", text, re.MULTILINE)
    if not match:
        return ""
    value = match.group(1).strip().strip("`'\" ")
    return "" if value.startswith("<") else value


def safe_text(text: str) -> str:
    """Remove control characters (ESC, BEL, newlines, ...) so student-written text cannot steer a terminal."""
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)


def all_step_commands(text: str) -> Dict[str, List[str]]:
    """The commands the template names in the header line of every step ('--- 6.3  rm -i old_motor.c   then   ls ---')."""
    found: Dict[str, List[str]] = {}
    for line in text.split("\n"):
        match = HEADER_RE.match(line[:MAX_LINE])
        if match and match.group(1) not in found:
            found[match.group(1)] = [part.strip() for part in match.group(2).split(THEN) if part.strip()]
    return found


def step_commands(text: str, step_id: str) -> List[str]:
    """The commands of one step ([] if the step is not in the text)."""
    return all_step_commands(text).get(step_id, [])


MAX_CONTINUATION = 4   # physical lines one typed command can span (a folded command and its `>` prompts)
MAX_STARTS = 20        # places in one line where a typed command is tried (a prompt can hold the first word too)
HOME_FORMS = r"(?:~/|\$HOME/|/\S*?/)"  # how a student may write the home folder: ~/ , $HOME/ or the whole path


def _normal(text: str) -> str:
    """A shell line as one spelling: no quotes, one blank between words, none around && || | ;."""
    text = text.replace("'", "").replace('"', "")
    text = re.sub(r"\s*(&&|\|\||\||;)\s*", r"\1", text)
    return " ".join(text.split())


def _tail_pattern(command: str) -> "re.Pattern[str]":
    """The whole of a line that shows this command, in the normal spelling. The values a student types for the placeholders
    of the template (their name, their email) are matched by a wildcard, and ~/ by any way of writing the home folder."""
    body = re.escape(_normal(command))
    for placeholder in PLACEHOLDERS:
        body = body.replace(re.escape(placeholder), ".+?")
    return re.compile(body.replace(re.escape("~/"), HOME_FORMS))


def echo_prefix(line: str, commands: Sequence[str]) -> Optional[str]:
    """If 'line' is a prompt followed by one of the typed commands, the prompt before the command ('' for a bare command);
    None if it is not an echo of a typed command. The command must start after a space or a prompt sign, and may be spelt
    with other quotes or blanks than the template shows."""
    stripped = line[:MAX_LINE].strip()
    for command in sorted(commands, key=len, reverse=True):
        normal = _normal(command)
        if not normal:
            continue
        first, last = normal.split(" ", 1)[0], normal.rsplit(" ", 1)[-1].split("~/")[-1]  # the home folder may be written out
        if not any(mark in last for mark in ("Your Full Name", "your-email@your-college.edu")) and not _normal(stripped).endswith(last):
            continue  # cheap test first: a long line of something else is not worth trying at every start
        pattern, start, tried = _tail_pattern(command), stripped.find(first), 0
        while start != -1 and tried < MAX_STARTS:
            if (start == 0 or stripped[start - 1].isspace() or stripped[start - 1] in PROMPT_SIGNS) \
                    and pattern.fullmatch(_normal(stripped[start:])):
                return stripped[:start].rstrip()
            start, tried = stripped.find(first, start + 1), tried + 1
    return None


def echo_span(lines: Sequence[str], index: int, commands: Sequence[str]) -> Optional[Tuple[int, str]]:
    """(how many lines, the prompt) when the lines from 'index' on show a typed command, None otherwise. A command folded
    with a trailing backslash is shown on several lines, the next ones after a `>` prompt: they are one echo."""
    joined = lines[index]
    for used in range(1, MAX_CONTINUATION + 1):
        prefix = echo_prefix(joined, commands)
        if prefix is not None:
            return used, prefix
        head = joined.rstrip()
        if not head.endswith(("\\", "&&")) or index + used >= len(lines):
            return None
        more = re.sub(r"^>\s*", "", lines[index + used].strip())
        joined = (head[:-1].rstrip() if head.endswith("\\") else head) + " " + more
    return None


def is_banner(line: str) -> bool:
    """The first line of Git Bash's two-line prompt: user@host MINGW64 ~/folder (branch)."""
    tokens = line[:MAX_LINE].split()
    return len(tokens) > 1 and "@" in tokens[0] and tokens[1].startswith(("MINGW", "MSYS", "UCRT", "CLANG"))


def _echoes(body: str, commands: Sequence[str]) -> "tuple[set[int], set[str]]":
    """The indexes of the lines of a step that are typed commands, and the prompts shown before them."""
    lines, consumed, prefixes, index = body.split("\n"), set(), set(), 0
    while index < len(lines):
        span = echo_span(lines, index, commands)
        if span is None:
            index += 1
            continue
        consumed.update(range(index, index + span[0]))
        if span[1]:
            prefixes.add(span[1])
        index += span[0]
    return consumed, prefixes


def strip_prompts(steps: Dict[str, str], text: str) -> Dict[str, str]:
    """The pasted steps without the lines a terminal copy adds around the output: the prompt with the typed command, and
    the prompt that waits after it (the same prompt text shows before every command, whatever shell the student uses)."""
    commands = all_step_commands(text)
    found = {step_id: _echoes(body, commands.get(step_id, [])) for step_id, body in steps.items()}
    prefixes = set().union(*(prefix for _, prefix in found.values())) if found else set()
    cleaned: Dict[str, str] = {}
    for step_id, body in steps.items():
        consumed = found[step_id][0]
        kept = [line for number, line in enumerate(body.split("\n"))
                if number not in consumed and line[:MAX_LINE].strip() not in prefixes and not is_banner(line)]
        cleaned[step_id] = "\n".join(kept).strip("\n")
    return cleaned
