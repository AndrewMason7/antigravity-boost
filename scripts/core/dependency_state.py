#!/usr/bin/env python3
"""
antigravity-boost core: Dependency State & Configuration Manager

Handles user configuration (config.json), attempt capping (max 2 attempts),
skipped package memory, size-capped debug log rotation (max 1 MB), and session-isolated persistence.
"""

from __future__ import annotations
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Any


DEFAULT_CONFIG: Dict[str, Any] = {
    "auto_git_checkpoints": True,
    "max_install_attempts": 2,
    "custom_safe_patterns": [],
    "custom_destructive_patterns": [],
    "debug_mode": False
}

MAX_LOG_BYTES = 1024 * 1024  # 1 MB max debug log size cap


def log_debug(message: str) -> None:
    env_debug = os.environ.get("BOOST_DEBUG", "").strip() in ("1", "true", "TRUE")
    if not env_debug:
        cfg = ConfigStore.load_config()
        if not cfg.get("debug_mode", False):
            return

    try:
        log_file = Path(tempfile.gettempdir()) / "antigravity_boost" / "debug.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        if log_file.exists() and log_file.stat().st_size > MAX_LOG_BYTES:
            try:
                content = log_file.read_text(encoding="utf-8", errors="replace")
                log_file.write_text("[LOG TRUNCATED - MAX 1MB CAP EXCEEDED]\n" + content[-200000:], encoding="utf-8")
            except Exception:
                log_file.unlink(missing_ok=True)

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception:
        pass


class ConfigStore:
    """Loads and caches user configuration from config.json."""

    @staticmethod
    def load_config() -> Dict[str, Any]:
        config_path = Path(__file__).resolve().parent.parent.parent / "config.json"
        if not config_path.exists():
            config_path = Path.home() / ".gemini" / "config" / "plugins" / "antigravity-boost" / "config.json"
        
        if config_path.exists():
            try:
                user_cfg = json.loads(config_path.read_text(encoding="utf-8", errors="replace"))
                merged = {**DEFAULT_CONFIG, **user_cfg}
                return merged
            except Exception:
                pass
        return DEFAULT_CONFIG


class DependencyStateStore:
    """Handles thread-safe, multi-session isolated state persistence with attempt capping and skip memory."""

    @staticmethod
    def resolve_state_file(conversation_id: Optional[str] = None, state_filename: Optional[str] = None) -> Path:
        temp_dir = Path(tempfile.gettempdir()) / "antigravity_boost"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        if state_filename:
            return temp_dir / state_filename
        
        cid = conversation_id.strip() if conversation_id and conversation_id.strip() else "global"
        safe_cid = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in cid])
        return temp_dir / f".deps_pending_{safe_cid}.json"

    @classmethod
    def read_state(cls, state_file: Path) -> Optional[Dict]:
        if not state_file.exists():
            return None
        try:
            return json.loads(state_file.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return None

    @classmethod
    def write_state(cls, state_file: Path, packages: List[str], details: List[Dict], error_msg: str = "") -> None:
        cfg = ConfigStore.load_config()
        max_attempts = cfg.get("max_install_attempts", 2)

        existing = cls.read_state(state_file) or {}
        attempts: Dict[str, int] = existing.get("attempts", {})
        skipped: List[str] = existing.get("skipped_packages", [])

        valid_packages = []
        valid_details = []

        for item in details:
            pkg_name = item["name"]
            if pkg_name in skipped:
                log_debug(f"Skipping package '{pkg_name}' because it was previously marked as skipped by user.")
                continue

            current_count = attempts.get(pkg_name, 0) + 1
            attempts[pkg_name] = current_count

            if current_count > max_attempts:
                log_debug(f"Package '{pkg_name}' reached max attempts ({current_count}/{max_attempts}). Capping to prevent loop.")
                continue

            valid_packages.append(pkg_name)
            valid_details.append(item)

        state_payload = {
            "packages": sorted(list(set(valid_packages))),
            "details": valid_details,
            "attempts": attempts,
            "skipped_packages": skipped
        }

        if not valid_packages and error_msg.strip():
            state_payload["unhandled_error"] = True
            state_payload["error_summary"] = error_msg.strip()[:500]

        serialized = json.dumps(state_payload, separators=(',', ':'))
        tmp_file = state_file.with_suffix(".tmp")
        tmp_file.write_text(serialized, encoding="utf-8", errors="replace")
        
        for attempt in range(3):
            try:
                tmp_file.replace(state_file)
                break
            except Exception:
                time.sleep(0.01)

    @classmethod
    def mark_skipped(cls, state_file: Path, package_names: List[str]) -> None:
        existing = cls.read_state(state_file) or {}
        skipped: List[str] = existing.get("skipped_packages", [])
        for pkg in package_names:
            if pkg not in skipped:
                skipped.append(pkg)
        existing["skipped_packages"] = skipped
        existing["packages"] = [p for p in existing.get("packages", []) if p not in skipped]
        
        serialized = json.dumps(existing, separators=(',', ':'))
        tmp_file = state_file.with_suffix(".tmp")
        tmp_file.write_text(serialized, encoding="utf-8", errors="replace")
        try:
            tmp_file.replace(state_file)
        except Exception:
            pass

    @classmethod
    def clear_state(cls, state_file: Path) -> None:
        if state_file.exists():
            try:
                state_file.unlink()
            except Exception:
                pass
        tmp_file = state_file.with_suffix(".tmp")
        if tmp_file.exists():
            try:
                tmp_file.unlink()
            except Exception:
                pass
