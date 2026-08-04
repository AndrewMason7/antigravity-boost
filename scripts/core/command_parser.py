#!/usr/bin/env python3
"""
antigravity-flow core: Command Parser

High-performance, shell-aware parser for splitting shell command strings,
normalizing Unicode homoglyphs (NFKC), and detecting subshell/envvar substitution ($(), backticks, $VAR).
"""

from __future__ import annotations
import re
import shlex
import unicodedata
from typing import List, Tuple


class CommandParser:
    """Parses shell command strings into sub-commands with Unicode & subshell security checks."""

    OPERATOR_CHARS = {'&', '|', ';'}
    OPERATOR_PATTERN = re.compile(r"\s*(?:&&|\|\||;|\|)\s*")
    SUBSHELL_PATTERN = re.compile(r"(?:\$\(|=|`|\beval\b|\bbash\s+-c\b|\bsh\s+-c\b|\$\{[a-zA-Z0-9_]+\}|\$[a-zA-Z_][a-zA-Z0-9_]*)")

    @classmethod
    def normalize_unicode(cls, text: str) -> str:
        """Normalizes Unicode homoglyphs to standard ASCII NFKC form to prevent bypass tricks."""
        if not text:
            return ""
        return unicodedata.normalize("NFKC", text)

    @classmethod
    def has_subshell_substitution(cls, command_line: str) -> bool:
        """Detects subshell command substitution ($(), backticks, eval, $VAR) in command_line safely."""
        if not command_line:
            return False
        normalized = cls.normalize_unicode(command_line)
        try:
            if cls.SUBSHELL_PATTERN.search(normalized):
                return True
            shlex.split(normalized)
            return False
        except ValueError:
            return True
        except Exception:
            return False

    @classmethod
    def split_subcommands(cls, command_line: str) -> List[str]:
        if not command_line:
            return []
        
        normalized = cls.normalize_unicode(command_line.strip())
        if not normalized:
            return []

        try:
            if not any(char in normalized for char in cls.OPERATOR_CHARS):
                return [normalized]

            tokens = cls.OPERATOR_PATTERN.split(normalized)
            return [t.strip() for t in tokens if t.strip()]
        except Exception:
            return [normalized]
