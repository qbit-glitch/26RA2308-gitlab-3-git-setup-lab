#!/usr/bin/env python3
"""Automatic grader for the Git Setup lab.

Usage (from any folder; the command names your clone):
    python3 ~/git-setup-lab/tests/grade.py           # grade submission/outputs.txt against this computer and your clone
    python3 tests/grade.py --outputs-only            # grade only the pasted text (no checks of this computer)
    python3 tests/grade.py --home DIR                # look for ~/.gitconfig and ~/.ssh in DIR instead of your home folder
    python3 tests/grade.py --submission path/to/outputs.txt --repo path/to/clone

Exit status is 0 when every task passes, 1 otherwise, 2 for set-up problems.
The grader only reads files: your global git settings, your clone's settings and your PUBLIC key (never your private key).
It never runs git, ssh or anything you wrote.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from typing import List, Optional

sys.dont_write_bytecode = True  # grading must never leave __pycache__ folders in your clone
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from autograde.context import Ctx  # noqa: E402
from autograde.facts import Facts  # noqa: E402
from autograde.framework import Task, format_report  # noqa: E402
from autograde.integrity import integrity_warnings  # noqa: E402
from autograde.tasks_a import grade_task1, grade_task2, grade_task3, grade_task4  # noqa: E402
from autograde.tasks_b import grade_task5, grade_task6, grade_task7  # noqa: E402
from autograde.textutil import header_field, normalise, parse_steps, safe_text, strip_prompts  # noqa: E402

REPO_ROOT = os.path.dirname(HERE)
DEFAULT_SUBMISSION = os.path.join(REPO_ROOT, "submission", "outputs.txt")
DEFAULT_REPORT = os.path.join(REPO_ROOT, "submission", "results.txt")
MAX_SUBMISSION = 1 << 20  # read at most 1 MiB of a submission: a real one is a few kilobytes
GRADERS = [grade_task1, grade_task2, grade_task3, grade_task4, grade_task5, grade_task6, grade_task7]


def write_report(target: str, content: str) -> None:
    """Write the report file, but never through a link: a student's folder could point results.txt elsewhere."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(target, flags, 0o644)
    except OSError:
        print(f"note: {os.path.basename(target)} was not written (it is a link or cannot be written)")
        return
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(content)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Read the command-line options."""
    parser = argparse.ArgumentParser(description="Grade the Git Setup lab.")
    parser.add_argument("--submission", default=DEFAULT_SUBMISSION, help="pasted-outputs file")
    parser.add_argument("--repo", default=REPO_ROOT, help="the student's clone (default: this repo)")
    parser.add_argument("--home", default=None, help="the home folder to look in for .gitconfig and .ssh (default: yours)")
    parser.add_argument("--outputs-only", action="store_true",
                        help="skip checks that need the live folders (for grading a submitted file)")
    parser.add_argument("--no-report", action="store_true", help="do not write submission/results.txt")
    parser.add_argument("--report", default=None,
                        help="where to write the report (default: submission/results.txt, only for the default submission)")
    parser.add_argument("--brief", action="store_true", help="only list checks that failed")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Run all task graders and print the report."""
    args = parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # a console with a small code page must print "?" for a letter it lacks, not crash
        try:
            stream.reconfigure(errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            pass
    if not os.path.isfile(args.submission):
        print(f"Submission file not found: {args.submission}\n"
              "Create it with:  cp submission/outputs.template.txt submission/outputs.txt")
        return 2
    facts = Facts(None if args.outputs_only else args.repo, args.home)
    with open(args.submission, encoding="utf-8-sig", errors="replace") as handle:
        raw = handle.read(MAX_SUBMISSION + 1)
    if len(raw) > MAX_SUBMISSION:
        print("note: only the first 1 MiB of the submission was read")
    text = normalise(raw[:MAX_SUBMISSION])
    ctx = Ctx(steps=strip_prompts(parse_steps(text), text), text=text, facts=facts, repo_mode=not args.outputs_only)

    tasks: List[Task] = []
    for grader in GRADERS:
        task = grader(ctx)
        task.validate()
        tasks.append(task)

    who = safe_text(header_field(text, "Name")) or "(name not filled in)"
    header = [
        "Git Setup Lab - automatic grader",
        f"Student : {who}",
        f"Mode    : {'outputs-only (no checks of this computer)' if args.outputs_only else 'full (pasted outputs + this computer + your clone)'}",
        f"Graded  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    report = format_report(tasks, header, verbose=not args.brief)
    for warning in integrity_warnings(ctx):
        report += f"\nINTEGRITY WARNING: {safe_text(warning)}"
    print(report)
    default_submission = os.path.abspath(args.submission) == os.path.abspath(DEFAULT_SUBMISSION)
    target = args.report or (DEFAULT_REPORT if default_submission else None)  # never a file next to someone else's submission
    if target and not args.no_report and not args.outputs_only:
        write_report(target, report + "\n")
    return 0 if all(task.passed for task in tasks) else 1


if __name__ == "__main__":
    sys.exit(main())
