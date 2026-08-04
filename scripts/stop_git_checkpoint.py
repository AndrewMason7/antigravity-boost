#!/usr/bin/env python3
"""
antigravity-boost: Stop Event Git Checkpoint Controller

Executes automatic Git WIP checkpoints on model termination if auto_git_checkpoints is enabled in config.json.
Enforces timeout=3 on all subprocess calls to prevent infinite hanging on SSH/GPG prompts.
Supplies fallback Git identity environment variables so commits never fail on unconfigured machines.
Amends the previous commit if it was already a wip(boost) commit to prevent git log pollution.
Excludes internal plugin state files (.deps_pending*).
"""

from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from core.dependency_state import ConfigStore, log_debug

if hasattr(sys.stdin, "reconfigure"):
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": os.environ.get("GIT_AUTHOR_NAME", "Antigravity Boost"),
    "GIT_AUTHOR_EMAIL": os.environ.get("GIT_AUTHOR_EMAIL", "boost@antigravity.local"),
    "GIT_COMMITTER_NAME": os.environ.get("GIT_COMMITTER_NAME", "Antigravity Boost"),
    "GIT_COMMITTER_EMAIL": os.environ.get("GIT_COMMITTER_EMAIL", "boost@antigravity.local")
}


def is_git_repository() -> bool:
    try:
        proc = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True, env=GIT_ENV, timeout=3)
        return proc.returncode == 0 and proc.stdout.strip() == "true"
    except Exception:
        return False


def is_last_commit_wip() -> bool:
    try:
        proc = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, env=GIT_ENV, timeout=3)
        if proc.returncode == 0:
            msg = proc.stdout.strip()
            return msg.startswith("wip(boost):") or msg.startswith("wip(flow):")
    except Exception:
        pass
    return False


def main():
    try:
        cfg = ConfigStore.load_config()
        if not cfg.get("auto_git_checkpoints", True):
            log_debug("Auto Git checkpoints disabled in config.json. Skipping checkpoint.")
            print(json.dumps({"decision": "allow"}))
            return

        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
        reason = payload.get("terminationReason", "")

        if reason == "model_stop" and is_git_repository():
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, env=GIT_ENV, timeout=3)
            if status.returncode == 0 and status.stdout.strip():
                subprocess.run(["git", "add", "-A"], capture_output=True, env=GIT_ENV, timeout=3)
                subprocess.run(["git", "reset", "--", ".deps_pending.json", ".deps_pending.tmp"], capture_output=True, env=GIT_ENV, timeout=3)
                
                staged = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, env=GIT_ENV, timeout=3)
                if staged.returncode == 0 and staged.stdout.strip():
                    if is_last_commit_wip():
                        subprocess.run(["git", "commit", "--amend", "--no-edit"], capture_output=True, env=GIT_ENV, timeout=3)
                    else:
                        subprocess.run(["git", "commit", "-m", "wip(boost): auto-checkpoint after task completion"], capture_output=True, env=GIT_ENV, timeout=3)

        print(json.dumps({"decision": "allow"}))
    except Exception:
        print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
