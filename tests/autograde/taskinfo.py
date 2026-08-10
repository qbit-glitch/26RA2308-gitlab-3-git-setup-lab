"""Titles, marks and fixed texts of the seven lab tasks (the grader cannot import the instructor kit, so they are repeated here)."""
from __future__ import annotations

from typing import Dict, Tuple

TITLES: Dict[int, str] = {
    1: "Is Git here", 2: "Who are you", 3: "Defaults", 4: "Where do the values come from", 5: "Two emails, one folder",
    6: "Shortcuts", 7: "SSH key",
}
MARKS: Dict[int, int] = {1: 8, 2: 14, 3: 12, 4: 16, 5: 14, 6: 16, 7: 20}

CLONE = "git-setup-lab"
MIN_VERSION: Tuple[int, int] = (2, 28)  # the first Git with init.defaultBranch
LOCAL_EMAIL = "lab-only@kestrel.example"
ALIAS_LG = "log --oneline --graph --decorate --all"
PLACEHOLDER_NAMES = {"your full name", "your name", "full name", "name", "your name here"}
# the examples of the manual and of the handout, and the kinds of address nobody owns
PLACEHOLDER_EMAILS = {"yourname@dsu.edu.in", "your-email@your-college.edu", "you@example.com", "email@example.com",
                      "name@example.com", "user@example.com", "your@email.com", "your.email@example.com"}
PLACEHOLDER_LOCALS = {"yourname", "your-email", "your.email", "youremail", "you", "email", "name", "user", "username", "test",
                      "example", "abc", "xyz"}
PLACEHOLDER_DOMAINS = {"example.com", "example.org", "example.net", "your-college.edu", "email.com", "test.com", "domain.com"}
