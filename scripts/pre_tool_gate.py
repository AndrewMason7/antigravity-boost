#!/usr/bin/env python3
"""
antigravity-flow: PreToolUse Permission Gate Controller

Uses CommandParser and PatternMatcher to evaluate proposed tool executions.
"""

from __future__ import annotations
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

from core.command_parser import CommandParser
from core.pattern_matcher import PatternMatcher


def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"decision": "allow"}))
            return

        payload = json.loads(raw_input)
        tool_call = payload.get("toolCall", {})
        tool_name = tool_call.get("name", "")
        args = tool_call.get("args", {})

        if tool_name == "run_command":
            cmd = args.get("CommandLine", "")
            subcommands = CommandParser.split_subcommands(cmd)
            decision, reason = PatternMatcher.evaluate_command_line(subcommands, raw_command=cmd)
            
            response = {"decision": decision}
            if reason:
                response["reason"] = reason
            print(json.dumps(response))
            return

        print(json.dumps({"decision": "allow"}))
    except Exception:
        print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
