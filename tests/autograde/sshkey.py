"""SSH public keys and fingerprints, read as text. The private key is never read by the grader.

The fingerprint `ssh-keygen -lf` prints is `SHA256:` plus the base64 (without padding) of the SHA-256 of the key blob,
so it can be recomputed from the public key file and compared with what a student pasted.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import re
from typing import NamedTuple, Optional

MAX_LINE = 2000
KIND_RE = re.compile(r"^(ssh-[a-z0-9-]+|ecdsa-sha2-nistp\d+|sk-[a-z0-9@.-]+)$")
FINGERPRINT_RE = re.compile(r"SHA256:[A-Za-z0-9+/]+")


class PubKey(NamedTuple):
    """A parsed public key line."""

    kind: str
    blob: bytes
    comment: str
    fingerprint: str

    @property
    def is_ed25519(self) -> bool:
        """An ed25519 key: the kind, and the exact size of its blob (4 + 11 + 4 + 32 bytes)."""
        return self.kind == "ssh-ed25519" and len(self.blob) == 51


def fingerprint(blob: bytes) -> str:
    """The fingerprint ssh-keygen prints for this key blob."""
    return "SHA256:" + base64.b64encode(hashlib.sha256(blob).digest()).decode("ascii").rstrip("=")


def parse_public_key(text: str) -> Optional[PubKey]:
    """The key on the first line of a .pub file, or None if that line is not a public key."""
    first = (text.split("\n", 1)[0])[:MAX_LINE].strip()
    parts = first.split(None, 2)
    if len(parts) < 2 or not KIND_RE.match(parts[0]):
        return None
    try:
        blob = base64.b64decode(parts[1], validate=True)
    except (binascii.Error, ValueError):
        return None
    kind = parts[0].encode("ascii")
    if len(blob) < 4 + len(kind) or int.from_bytes(blob[:4], "big") != len(kind) or blob[4:4 + len(kind)] != kind:
        return None
    return PubKey(parts[0], blob, parts[2].strip() if len(parts) == 3 else "", fingerprint(blob))


def parse_fingerprint_line(text: str) -> Optional[str]:
    """The first SHA256:... fingerprint in what ssh-keygen printed (-lf, or the end of key generation), or None."""
    for raw in text.split("\n"):
        match = FINGERPRINT_RE.search(raw[:MAX_LINE])
        if match:
            return match.group(0)
    return None
