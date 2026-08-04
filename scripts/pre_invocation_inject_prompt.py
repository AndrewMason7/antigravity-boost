#!/usr/bin/env python3
"""
antigravity-flow: PreInvocation Injection Controller

Reads pending dependency state and formats PreInvocation trajectory injection steps.
Uses session-isolated state file resolution based on conversationId.
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# UTF-8 safe stdin reconfiguration
if hasattr(sys.stdin, "reconfigure"):
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from core.dependency_state import DependencyStateStore
from core.prompt_formatter import PromptFormatter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-file", default=None)
    args_parsed, _ = parser.parse_known_args()

    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
        cid = payload.get("conversationId", "global")
        
        state_file = Path(args_parsed.state_file) if args_parsed.state_file else DependencyStateStore.resolve_state_file(conversation_id=cid)
        state_data = DependencyStateStore.read_state(state_file)

        if not state_data:
            print(json.dumps(PromptFormatter.format_empty_response()))
            return

        packages = state_data.get("packages", [])
        unhandled_error = state_data.get("unhandled_error", False)
        error_summary = state_data.get("error_summary", "")

        if packages:
            res_payload = PromptFormatter.format_dependency_prompt(packages)
            DependencyStateStore.clear_state(state_file)
            print(json.dumps(res_payload))
            return

        if unhandled_error and error_summary:
            res_payload = PromptFormatter.format_unhandled_error_prompt(error_summary)
            DependencyStateStore.clear_state(state_file)
            print(json.dumps(res_payload))
            return

        print(json.dumps(PromptFormatter.format_empty_response()))
    except Exception:
        print(json.dumps(PromptFormatter.format_empty_response()))


if __name__ == "__main__":
    main()
