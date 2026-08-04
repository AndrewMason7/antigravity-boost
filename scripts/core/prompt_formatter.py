#!/usr/bin/env python3
"""
antigravity-flow core: Prompt Formatter

Responsible solely for formatting PreInvocation injection step payloads.
"""

from __future__ import annotations
from typing import Dict, List, Any


class PromptFormatter:
    """Formats PreInvocation ephemeral and tool call injection payloads."""

    @staticmethod
    def format_dependency_prompt(packages: List[str]) -> Dict[str, Any]:
        pkgs_str = ", ".join([f"'{p}'" for p in packages])
        message = (
            f"CRITICAL: Missing dependencies detected: [{pkgs_str}]. "
            f"You MUST immediately call the ask_question tool presenting clear options "
            f"to install all dependencies at once, install individually, or skip."
        )
        return {
            "injectSteps": [
                {
                    "ephemeralMessage": message
                }
            ]
        }

    @staticmethod
    def format_unhandled_error_prompt(error_summary: str) -> Dict[str, Any]:
        message = (
            f"CRITICAL: Command failed with unhandled error: '{error_summary[:200]}'. "
            f"DO NOT guess or fail silently. Immediately call the ask_question tool "
            f"presenting 2-3 plausible troubleshooting options to the user."
        )
        return {
            "injectSteps": [
                {
                    "ephemeralMessage": message
                }
            ]
        }

    @staticmethod
    def format_empty_response() -> Dict[str, Any]:
        return {"injectSteps": []}
