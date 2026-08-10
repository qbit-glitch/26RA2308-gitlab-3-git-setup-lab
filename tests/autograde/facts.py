"""Read-only facts about this computer and this clone: the global git settings, the clone's own settings, and the SSH key.

Nothing here runs git, ssh or anything a student wrote. The files are read as text and bounded in size. The *private*
key is never opened: only its existence and permissions are looked at. A symbolic link is followed for the home files
(dotfile managers make ~/.gitconfig a link, and the grader runs as the student anyway) and the content is never printed.
"""
from __future__ import annotations

import os
import stat
from typing import List, Mapping, Optional, Tuple

from . import gitconfig, sshkey

MAX_READ = 262144
GLOBAL_FILE = ".gitconfig"


class Facts:
    """Live facts (repo=None means there is no clone and no computer to look at: only pasted text can be judged)."""

    def __init__(self, repo: Optional[str], home: Optional[str] = None, env: Optional[Mapping[str, str]] = None) -> None:
        self.repo = os.path.abspath(repo) if repo and os.path.isdir(repo) else None
        self.explicit_home = home is not None
        self.home = os.path.abspath(home) if home else os.path.expanduser("~")
        self.env = os.environ if env is None else env

    # -- files -------------------------------------------------------------------------------------
    @staticmethod
    def read_text(path: str) -> Optional[str]:
        """The first 256 KiB of a regular file (after following a link), or None for anything else."""
        try:
            if not stat.S_ISREG(os.stat(path).st_mode):
                return None
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
        except (OSError, ValueError):
            return None
        with os.fdopen(descriptor, "rb") as handle:
            return handle.read(MAX_READ).decode("utf-8", errors="replace")

    def global_files(self) -> List[str]:
        """The files `git config --global` reads, lowest priority first: GIT_CONFIG_GLOBAL alone when it is set,
        else the XDG file and then ~/.gitconfig (a home given on the command line ignores the environment)."""
        if not self.explicit_home and self.env.get("GIT_CONFIG_GLOBAL"):
            return [self.env["GIT_CONFIG_GLOBAL"]]
        xdg = self.env.get("XDG_CONFIG_HOME") if not self.explicit_home else None
        return [os.path.join(xdg or os.path.join(self.home, ".config"), "git", "config"), os.path.join(self.home, GLOBAL_FILE)]

    def _global_entries(self) -> List[Tuple[str, str, str]]:
        found: List[Tuple[str, str, str]] = []
        for path in self.global_files():
            text = self.read_text(path)
            if text is not None:
                found += [(key, value or "", path) for key, value in gitconfig.parse(text)]
        return found

    def global_value(self, key: str) -> Optional[str]:
        """What `git config --global key` prints: the last value over the global files, or None."""
        values = [value for k, value, _ in self._global_entries() if k == key.lower()]
        return values[-1] if values else None

    def global_origin(self, key: str) -> Optional[str]:
        """The global file that holds the last definition of the key, or None."""
        paths = [path for k, _, path in self._global_entries() if k == key.lower()]
        return paths[-1] if paths else None

    def local_text(self) -> Optional[str]:
        """The text of the clone's own .git/config, or None."""
        return self.read_text(os.path.join(self.repo, ".git", "config")) if self.repo else None

    def local_has(self, key: str) -> Optional[bool]:
        """Does .git/config define the key? None when the file cannot be read."""
        text = self.local_text()
        return None if text is None else key.lower() in gitconfig.values(text)

    # -- SSH key -----------------------------------------------------------------------------------
    def pub_key(self) -> Optional[sshkey.PubKey]:
        """The key in ~/.ssh/id_ed25519.pub, or None."""
        text = self.read_text(os.path.join(self.home, ".ssh", "id_ed25519.pub"))
        return sshkey.parse_public_key(text) if text is not None else None

    def private_key_mode(self) -> Optional[int]:
        """The permission bits of ~/.ssh/id_ed25519, or None if there is no such file. The file is never opened."""
        try:
            info = os.stat(os.path.join(self.home, ".ssh", "id_ed25519"))
        except (OSError, ValueError):
            return None
        return stat.S_IMODE(info.st_mode) if stat.S_ISREG(info.st_mode) else None

    # -- the rest ----------------------------------------------------------------------------------
    @staticmethod
    def exists(path: str) -> bool:
        """Is there a file or folder at this path on this computer?"""
        try:
            return os.path.exists(path)
        except (OSError, ValueError):
            return False

    @staticmethod
    def same_file(first: str, second: str) -> bool:
        """Are the two paths the same file on this computer? (False for anything that cannot be told.)"""
        try:
            return os.path.samefile(first, second)
        except (OSError, ValueError):
            return False
