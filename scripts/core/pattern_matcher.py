#!/usr/bin/env python3
"""
antigravity-flow core: Pattern Matcher

High-performance pattern matcher using pre-compiled, ReDoS-immune bounded regex,
path prefix matching (/bin/rm, sudo rm), redirection safety (> file), Unicode NFKC form,
subshell evaluation, plain-English reasons, and user config.json pattern extensions.
"""

from __future__ import annotations
import re
from typing import List, Tuple
from core.command_parser import CommandParser
from core.dependency_state import ConfigStore, log_debug


SAFE_COMPILED = re.compile(
    r"^\s*(?:sudo\s+)?(?:"
    r"git\s+(?:status|diff|log|branch|show)|"
    r"(?:npm|pnpm|yarn|bun)\s+(?:test|run\s+test|check)|"
    r"(?:pytest|cargo\s+check|go\s+test)|"
    r"(?:ls|cat|pwd|whoami|echo)"
    r")\b",
    re.IGNORECASE
)

DESTRUCTIVE_PATTERNS = [
    (re.compile(r"(?:/bin/|/usr/bin/|\\)?\brm\s+-rf?\b", re.IGNORECASE), "This command permanently deletes files/directories (`rm -rf`)."),
    (re.compile(r"(?:/bin/|/usr/bin/|\\)?\bgit\s+reset\s+--hard\b", re.IGNORECASE), "This command discards all uncommitted local code changes (`git reset --hard`)."),
    (re.compile(r"(?:/bin/|/usr/bin/|\\)?\bgit\s+push\s+[^;&]*?(?:-f\b|--force)\b", re.IGNORECASE), "This command force-overwrites remote Git history (`git push --force`)."),
    (re.compile(r"\bdrop\s+database\b", re.IGNORECASE), "This command permanently deletes a database (`DROP DATABASE`)."),
    (re.compile(r"\bformat\s+[c-z]:\b", re.IGNORECASE), "This command formats a disk drive."),
    (re.compile(r"\bdd\s+if=", re.IGNORECASE), "This command performs raw block device overwrite (`dd if=`)."),
    (re.compile(r"(?:>|>\|)\s*[^/][^\s]+", re.IGNORECASE), "This command uses output redirection (`>`) which can truncate existing files.")
]


class PatternMatcher:
    """Evaluates sub-command security & diagnostic classification with security audit hardening."""

    @staticmethod
    def is_destructive(subcommand: str, custom_destructive: List[str] = None) -> Tuple[bool, str]:
        normalized = CommandParser.normalize_unicode(subcommand)

        for pattern, explanation in DESTRUCTIVE_PATTERNS:
            if pattern.search(normalized):
                return True, f"Security Warning: {explanation} Please confirm if you want to proceed."
        
        if custom_destructive:
            for pat in custom_destructive:
                try:
                    if re.search(pat, normalized, re.IGNORECASE):
                        return True, f"Security Warning: Subcommand matches custom destructive pattern '{pat}' from config.json. Please confirm."
                except Exception as e:
                    log_debug(f"Invalid custom destructive regex '{pat}': {e}")
        return False, ""

    @staticmethod
    def is_safe(subcommand: str, custom_safe: List[str] = None) -> bool:
        normalized = CommandParser.normalize_unicode(subcommand)
        if SAFE_COMPILED.search(normalized):
            return True
        if custom_safe:
            for pat in custom_safe:
                try:
                    if re.search(pat, normalized, re.IGNORECASE):
                        return True
                except Exception as e:
                    log_debug(f"Invalid custom safe regex '{pat}': {e}")
        return False

    @classmethod
    def evaluate_command_line(cls, subcommands: List[str], raw_command: str = "") -> Tuple[str, str]:
        if not subcommands:
            return "allow", ""

        cfg = ConfigStore.load_config()
        custom_safe = cfg.get("custom_safe_patterns", [])
        custom_destructive = cfg.get("custom_destructive_patterns", [])

        normalized_raw = CommandParser.normalize_unicode(raw_command)
        if normalized_raw and CommandParser.has_subshell_substitution(normalized_raw):
            return "ask", "Security Warning: Command contains subshell or environment variable substitution ($(), backticks, $VAR) which executes nested logic. Please confirm."

        for sub in subcommands:
            destructive, reason = cls.is_destructive(sub, custom_destructive)
            if destructive:
                return "ask", reason

        all_safe = all(cls.is_safe(sub, custom_safe) for sub in subcommands)
        if all_safe:
            return "allow", ""

        return "allow", ""
