#!/usr/bin/env python3
"""
antigravity-flow: Interactive Auto-Dependency Detector Script

High-performance, modular dependency detector supporting Python, Node/TS,
Rust, Go, C/C++ Headers, and System CLI tools with PEP 668 Homebrew Python
compatibility, cross-platform OS detection, sub-namespace PyPI mappings,
and session-isolated state files.
"""

from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from core.dependency_state import DependencyStateStore


# ==============================================================================
# Standard Library Exclusion Lists
# ==============================================================================

PYTHON_STDLIB: Set[str] = {
    "sys", "os", "json", "re", "math", "typing", "asyncio", "datetime", "collections",
    "functools", "itertools", "urllib", "sqlite3", "subprocess", "random", "hashlib",
    "shutil", "tempfile", "unittest", "logging", "csv", "xml", "base64", "struct",
    "socket", "platform", "dataclasses", "enum", "pathlib", "select", "signal",
    "threading", "multiprocessing", "time", "copy", "glob", "io", "inspect",
    "pprint", "traceback", "zipfile", "tarfile", "gzip", "bz2", "configparser",
    "argparse", "optparse", "getopt", "shlex", "ast", "dis", "code", "string",
    "numbers", "decimal", "fractions", "cmath", "array", "queue", "heapq", "bisect",
    "weakref", "types", "gc", "sysconfig", "importlib", "site", "__future__",
    "ctypes", "codecs", "socketserver", "http", "email", "html", "wsgiref",
    "tkinter", "curses", "dbm", "sqlite3", "readline", "rlcompleter"
}

NODE_BUILTINS: Set[str] = {
    "fs", "path", "http", "https", "events", "crypto", "stream", "util",
    "child_process", "os", "assert", "url", "net", "tls", "dns", "zlib",
    "readline", "cluster", "dgram", "module", "process", "buffer", "v8",
    "vm", "worker_threads", "perf_hooks", "node:fs", "node:path", "node:http",
    "node:https", "node:events", "node:crypto", "node:stream", "node:util",
    "node:child_process", "node:os", "node:assert", "node:url", "node:net",
    "node:buffer", "node:process", "node:test"
}

RUST_STDLIB: Set[str] = {"std", "core", "alloc", "proc_macro", "test"}

GO_STDLIB: Set[str] = {
    "fmt", "os", "net", "http", "io", "time", "strings", "bytes", "context",
    "sync", "encoding", "json", "log", "errors", "testing", "math", "sort",
    "path", "flag", "regexp", "bufio", "html", "template", "reflect", "runtime",
    "database", "crypto", "archive", "compress", "container", "debug"
}


# ==============================================================================
# Ecosystem Mappings & Canonical Aliases
# ==============================================================================

PYTHON_PYPI_MAP: Dict[str, str] = {
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "bs4": "beautifulsoup4",
    "sklearn": "scikit-learn",
    "skimage": "scikit-image",
    "yaml": "pyyaml",
    "dotenv": "python-dotenv",
    "dateutil": "python-dateutil",
    "attr": "attrs",
    "serial": "pyserial",
    "jwt": "PyJWT",
    "fitz": "PyMuPDF",
    "wx": "wxPython",
    "gi": "PyGObject",
    "OpenGL": "PyOpenGL",
    "magic": "python-magic",
    "crypto": "pycryptodome",
    "Crypto": "pycryptodome",
    "docx": "python-docx",
    "pptx": "python-pptx",
    "openpyxl": "openpyxl",
    "xlsxwriter": "XlsxWriter",
    "psycopg2": "psycopg2-binary",
    "mysql": "mysql-connector-python",
    "soundfile": "soundfile",
    "librosa": "librosa",
    "moviepy": "moviepy",
    "reportlab": "reportlab",
    "pylab": "matplotlib",
    "matplotlib": "matplotlib",
    "torch": "torch",
    "torchvision": "torchvision",
    "torchaudio": "torchaudio",
    "tensorflow": "tensorflow",
    "transformers": "transformers",
    "datasets": "datasets",
    "accelerate": "accelerate",
    "diffusers": "diffusers",
    "huggingface_hub": "huggingface-hub",
    "gradio": "gradio",
    "streamlit": "streamlit",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "pydantic": "pydantic",
    "boto3": "boto3",
    "botocore": "botocore",
    "google.cloud.storage": "google-cloud-storage",
    "google.cloud.bigquery": "google-cloud-bigquery",
    "google.cloud.firestore": "google-cloud-firestore",
    "google.cloud": "google-cloud-storage",
    "azure.storage.blob": "azure-storage-blob",
    "azure.identity": "azure-identity",
    "azure": "azure-storage-blob",
    "playwright": "playwright",
    "selenium": "selenium",
    "scrapy": "scrapy",
    "celery": "celery",
    "redis": "redis",
    "pymongo": "pymongo",
    "sqlalchemy": "SQLAlchemy",
    "alembic": "alembic",
    "pandas": "pandas",
    "polars": "polars",
    "duckdb": "duckdb",
    "numpy": "numpy",
    "scipy": "scipy",
    "seaborn": "seaborn",
    "plotly": "plotly",
    "networkx": "networkx",
    "bokeh": "bokeh",
    "dash": "dash",
    "tornado": "tornado",
    "twisted": "twisted",
    "aiohttp": "aiohttp",
    "httpx": "httpx",
    "requests": "requests",
    "gevent": "gevent",
    "gunicorn": "gunicorn",
    "flask": "Flask",
    "django": "Django"
}

C_HEADER_MAP: Dict[str, str] = {
    "GL/gl.h": "opengl",
    "openssl/ssl.h": "openssl",
    "sqlite3.h": "sqlite3",
    "ffi.h": "libffi",
    "zlib.h": "zlib",
    "postgres.h": "postgresql",
    "libpq-fe.h": "postgresql",
    "png.h": "libpng",
    "jpeglib.h": "jpeg"
}

IGNORED_CLI_TOOLS: Set[str] = {
    "python", "python3", "node", "npm", "sh", "bash", "zsh", "cmd", "powershell", "env"
}


# ==============================================================================
# Cross-Platform OS Helper
# ==============================================================================

class OSPlatformHelper:
    @staticmethod
    def get_system_install_cmd(pkg: str) -> str:
        if sys.platform == "win32":
            return f"winget install {pkg}"
        elif sys.platform.startswith("linux"):
            return f"apt-get install -y {pkg}"
        else:
            return f"brew install {pkg}"


# ==============================================================================
# Package Manager Resolver with Monorepo CWD Traversal & PEP 668 Compatibility
# ==============================================================================

class PackageManagerResolver:
    @staticmethod
    def resolve_commands(cwd_path: Path = Path(".")) -> Tuple[str, str]:
        target_dir = cwd_path.resolve() if cwd_path.exists() else Path(".").resolve()
        
        node_cmd = "npm install"
        py_cmd = "python3 -m pip install"

        curr = target_dir
        for _ in range(5):
            if (curr / "pnpm-workspace.yaml").exists() or (curr / "pnpm-lock.yaml").exists():
                node_cmd = "pnpm add"
                break
            elif (curr / "yarn.lock").exists():
                node_cmd = "yarn add"
                break
            elif (curr / "bun.lockb").exists():
                node_cmd = "bun add"
                break
            if curr.parent == curr:
                break
            curr = curr.parent

        curr = target_dir
        is_venv = False
        for _ in range(5):
            venv_pip = curr / ".venv" / "bin" / "pip"
            if venv_pip.exists():
                py_cmd = f"{venv_pip} install"
                is_venv = True
                break
            elif (curr / "poetry.lock").exists() or (curr / "pyproject.toml").exists():
                py_cmd = "poetry add"
                is_venv = True
                break
            elif (curr / "uv.lock").exists():
                py_cmd = "uv add"
                is_venv = True
                break
            elif (curr / "Pipfile").exists():
                py_cmd = "pipenv install"
                is_venv = True
                break
            if curr.parent == curr:
                break
            curr = curr.parent

        # If system Python on macOS without virtualenv, add PEP 668 --break-system-packages flag
        if not is_venv and sys.platform == "darwin":
            py_cmd = "python3 -m pip install --break-system-packages"

        return node_cmd, py_cmd


# ==============================================================================
# Ecosystem Detector Classes
# ==============================================================================

class BaseDetector:
    def detect(self, error_msg: str, workspace_dir: Path) -> List[Dict]:
        raise NotImplementedError


class PythonDetector(BaseDetector):
    def detect(self, error_msg: str, workspace_dir: Path) -> List[Dict]:
        _, py_cmd = PackageManagerResolver.resolve_commands(workspace_dir)
        results = []

        patterns = [
            r"ModuleNotFoundError:\s+No module named ['\"]([^'\"]+)['\"]",
            r"ImportError:\s+cannot import name .* from ['\"]([^'\"]+)['\"]",
            r"ImportError:\s+No module named ['\"]?([a-zA-Z0-9_\-]+)['\"]?"
        ]

        found_modules = set()
        for p in patterns:
            for m in re.findall(p, error_msg):
                base_mod = m.split('.')[0]
                if base_mod and base_mod not in PYTHON_STDLIB:
                    local_file = workspace_dir / f"{base_mod}.py"
                    local_dir = workspace_dir / base_mod
                    if not (local_file.exists() or local_dir.exists()):
                        found_modules.add(m if m in PYTHON_PYPI_MAP else base_mod)

        for mod in found_modules:
            pypi_name = PYTHON_PYPI_MAP.get(mod, mod.split('.')[0])
            results.append({
                "name": pypi_name,
                "ecosystem": "python",
                "import_name": mod,
                "install_cmd": f"{py_cmd} {pypi_name}"
            })
        return results


class NodeDetector(BaseDetector):
    def detect(self, error_msg: str, workspace_dir: Path) -> List[Dict]:
        node_cmd, _ = PackageManagerResolver.resolve_commands(workspace_dir)
        results = []

        patterns = [
            r"Cannot find module ['\"]([^'\"]+)['\"]",
            r"ERR_MODULE_NOT_FOUND.*['\"]([^'\"]+)['\"]",
            r"TS2307:\s+Cannot find module ['\"]([^'\"]+)['\"]"
        ]

        found_packages = set()
        for p in patterns:
            for m in re.findall(p, error_msg):
                pkg = self._parse_node_package(m)
                if pkg:
                    found_packages.add((pkg, m))

        for pkg, raw_import in found_packages:
            results.append({
                "name": pkg,
                "ecosystem": "node",
                "import_name": raw_import,
                "install_cmd": f"{node_cmd} {pkg}"
            })
        return results

    @staticmethod
    def _parse_node_package(module_str: str) -> Optional[str]:
        if module_str.startswith('.') or module_str.startswith('~') or module_str.startswith('@/'):
            return None
        if module_str in NODE_BUILTINS:
            return None
        parts = module_str.split('/')
        if module_str.startswith('@'):
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1]}"
            return module_str
        return parts[0]


class CHeaderDetector(BaseDetector):
    def detect(self, error_msg: str, workspace_dir: Path) -> List[Dict]:
        results = []
        patterns = [
            r"fatal error:\s*['\"]([^'\"]+)['\"]\s*file not found",
            r"fatal error:\s*([^:\s]+):\s*No such file or directory"
        ]
        for p in patterns:
            for h in re.findall(p, error_msg, re.IGNORECASE):
                pkg = C_HEADER_MAP.get(h, h.split('/')[0].replace('.h', ''))
                install_cmd = OSPlatformHelper.get_system_install_cmd(pkg)
                results.append({
                    "name": pkg,
                    "ecosystem": "c_header",
                    "import_name": h,
                    "install_cmd": install_cmd
                })
        return results


class RustDetector(BaseDetector):
    def detect(self, error_msg: str, workspace_dir: Path) -> List[Dict]:
        results = []
        patterns = [
            r"unresolved import [`']([^`']+)[`']",
            r"use of undeclared crate or module [`']([^`']+)[`']"
        ]
        for p in patterns:
            for m in re.findall(p, error_msg):
                crate = m.split('::')[0]
                if crate and crate not in RUST_STDLIB:
                    results.append({
                        "name": crate,
                        "ecosystem": "rust",
                        "import_name": crate,
                        "install_cmd": f"cargo add {crate}"
                    })
        return results


class GoDetector(BaseDetector):
    def detect(self, error_msg: str, workspace_dir: Path) -> List[Dict]:
        results = []
        patterns = [
            r"no required module provides package ([a-zA-Z0-9_\-\.\/]+)",
            r"cannot find package [\"']([^\"']+)[\"']"
        ]
        for p in patterns:
            for m in re.findall(p, error_msg):
                base_pkg = m.split('/')[0]
                if base_pkg not in GO_STDLIB and '.' in base_pkg:
                    results.append({
                        "name": m,
                        "ecosystem": "go",
                        "import_name": m,
                        "install_cmd": f"go get {m}"
                    })
        return results


class SystemCLIDetector(BaseDetector):
    def detect(self, error_msg: str, workspace_dir: Path) -> List[Dict]:
        results = []
        patterns = [
            r"(?:command not found|is not recognized):\s*([a-zA-Z0-9_\-]+)",
            r"sh:\s*([a-zA-Z0-9_\-]+):\s*command not found"
        ]
        for p in patterns:
            for cli in re.findall(p, error_msg, re.IGNORECASE):
                cli_clean = cli.lower().strip()
                if cli_clean and cli_clean not in IGNORED_CLI_TOOLS:
                    install_cmd = OSPlatformHelper.get_system_install_cmd(cli_clean)
                    results.append({
                        "name": cli_clean,
                        "ecosystem": "system_cli",
                        "import_name": cli_clean,
                        "install_cmd": install_cmd
                    })
        return results


# ==============================================================================
# Main Orchestrator
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Antigravity Dependency Detector")
    parser.add_argument("--state-file", default=None)
    args_parsed, _ = parser.parse_known_args()

    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({}))
            return

        payload = json.loads(raw_input)
        error_msg = payload.get("error", "") or payload.get("output", "") or ""

        if not error_msg.strip():
            print(json.dumps({}))
            return

        cid = payload.get("conversationId", "global")
        tool_call = payload.get("toolCall", {})
        args = tool_call.get("args", {})
        cwd_str = args.get("Cwd", ".")
        workspace_dir = Path(cwd_str) if cwd_str else Path(".")

        detectors: List[BaseDetector] = [
            PythonDetector(),
            NodeDetector(),
            CHeaderDetector(),
            RustDetector(),
            GoDetector(),
            SystemCLIDetector()
        ]

        all_detected: List[Dict] = []
        for detector in detectors:
            all_detected.extend(detector.detect(error_msg, workspace_dir))

        state_file = Path(args_parsed.state_file) if args_parsed.state_file else DependencyStateStore.resolve_state_file(conversation_id=cid)
        if all_detected or error_msg.strip():
            DependencyStateStore.write_state(state_file, [d["name"] for d in all_detected], all_detected, error_msg)

        print(json.dumps({}))
    except Exception:
        print(json.dumps({}))

if __name__ == "__main__":
    main()
