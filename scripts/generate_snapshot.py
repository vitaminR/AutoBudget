#!/usr/bin/env python3
"""
Generate a token- and human-friendly project snapshot.
Run from the repository root.
- Skips node_modules, .git, and large/binary files
- Truncates long files and replaces binary data with placeholders
- Summarizes package-lock.json instead of dumping the whole tree
Produces: project_snapshot.md at repo root
"""
from __future__ import annotations
import os
import sys
import json
import re
import fnmatch
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def detect_repo_root() -> Path:
    """Use git to find the repo root; fallback to script's parent."""
    try:
        top = subprocess.check_output([
            "git", "rev-parse", "--show-toplevel"
        ], stderr=subprocess.DEVNULL).decode().strip()
        if top:
            return Path(top)
    except Exception:
        pass
    return Path(__file__).resolve().parents[1]

ROOT = detect_repo_root()
OUT = ROOT / "project_snapshot.md"
EXCLUDE_DIRS = {
    "node_modules", ".git", ".venv", "venv", "env",
    ".pytest_cache", ".mypy_cache", ".cache", "coverage",
    "dist", "build", ".next", "out", "target", "bin", "obj",
    ".gemini", ".vscode", "secrets", "db", "systemInstructions_files", "__pycache__", ".devlogs",
    # Exclude troubleshooting and cloud quota helpers from snapshots by default
    "tshoot_vertex", "gcloud_quota_check"
}
BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".pdf", ".zip", ".tar", ".gz", ".tgz", ".exe", ".dll", ".so", ".class", ".jar", ".woff", ".woff2", ".eot", ".ttf", ".pyc", ".pyo", ".pyd", ".wasm"}
LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}
SKIP_FILES = set(LOCKFILES)  # handled specially below

# Include-only policy for CRA public assets: keep only minimal docs
PUBLIC_DIR = ROOT / "autobudget_frontend" / "public"
PUBLIC_INCLUDE_ONLY = {"index.html", "manifest.json"}

# Extra sensitive filenames and globs to omit content for
SKIP_BASENAMES = {
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", ".env", ".env.local"
}
SKIP_GLOBS = [
    "*.env", "*.env.*", "*.pem", "*.key", "*.p12", "*.pfx", "*.cer", "*.crt",
    "*serviceAccount*.json", "*service-account*.json", "*credentials*.json", "*.key.json"
]
SENSITIVE_EXTS = {".csv", ".tsv", ".xlsx", ".xls", ".sqlite", ".db", ".db3", ".parquet"}
MAX_LINES = 300
MAX_BYTES = 200 * 1024  # 200 KB


def is_binary_path(p: Path) -> bool:
    return p.suffix.lower() in BINARY_EXTS


def looks_binary_file(p: Path, sample_size: int = 2048) -> bool:
    try:
        with p.open('rb') as fh:
            chunk = fh.read(sample_size)
        if not chunk:
            return False
        if b"\x00" in chunk:
            return True
        # crude printable ratio check
        text_bytes = bytes(range(32, 127)) + b"\n\r\t\f\b\x1b"
        printable = sum(b in text_bytes for b in chunk)
        return (printable / max(1, len(chunk))) < 0.7
    except Exception:
        return False


def is_sensitive_file(p: Path, text_sample: str | None = None) -> bool:
    """Heuristics to avoid including secrets at all."""
    if p.name in SKIP_BASENAMES:
        return True
    for pat in SKIP_GLOBS:
        if fnmatch.fnmatch(p.name, pat):
            return True
    # Any JSON file with "key" in the name is sensitive
    if p.suffix.lower() == ".json" and "key" in p.name.lower():
        return True
    # If it's a JSON that looks like a Google service account, skip
    if text_sample and p.suffix.lower() == ".json":
        if '"type"' in text_sample and 'service_account' in text_sample:
            return True
    if p.suffix.lower() in SENSITIVE_EXTS:
        return True
    return False


SECRET_PATTERNS: list[tuple[re.Pattern, str]] = [
    # PEM/OPENSSH private keys
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.MULTILINE), "[REDACTED PRIVATE KEY]"),
    # Google service account private_key field
    (re.compile(r'"private_key"\s*:\s*"-----BEGIN PRIVATE KEY-----[\s\S]+?END PRIVATE KEY-----"', re.MULTILINE), '"private_key": "[REDACTED]"'),
    # GitHub tokens
    (re.compile(r"ghp_[A-Za-z0-9]{36,}"), "[REDACTED_GH_TOKEN]"),
    # Google API keys
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "[REDACTED_GOOGLE_API_KEY]"),
    # AWS access key id
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED_AWS_ACCESS_KEY_ID]"),
    # AWS secret access key value in common formats
    (re.compile(r"(?i)(aws_?secret_?access_?key\s*[:=]\s*)(['\"]?)[A-Za-z0-9/+=]{40}\2"), r"\1[REDACTED_AWS_SECRET]"),
    # Generic Bearer tokens
    (re.compile(r"(?i)(Authorization\s*:\s*Bearer\s+)[A-Za-z0-9\.\-_]+"), r"\1[REDACTED]"),
    # x-api-key headers
    (re.compile(r"(?i)(x-api-key\s*:\s*)([^\s]+)"), r"\1[REDACTED]"),
    # Stripe keys
    (re.compile(r"sk_(?:live|test)_[A-Za-z0-9]{16,}"), "[REDACTED_STRIPE_SK]"),
    (re.compile(r"pk_(?:live|test)_[A-Za-z0-9]{16,}"), "[REDACTED_STRIPE_PK]"),
    # Slack tokens
    (re.compile(r"xox[abps]-[A-Za-z0-9-]{10,}"), "[REDACTED_SLACK]"),
    # Client email and private key id in service accounts
    (re.compile(r'"client_email"\s*:\s*"[^"]+"'), '"client_email": "[REDACTED_EMAIL]"'),
    (re.compile(r'"private_key_id"\s*:\s*"[^"]+"'), '"private_key_id": "[REDACTED]"'),
    # Common DB URLs
    (re.compile(r"(?i)\b(postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp|mssql|sqlserver)://[^\s\"]+"), r"\1://[REDACTED]")
]


def scrub_secrets(text: str) -> tuple[str, bool]:
    """Redact common secrets patterns from text content.
    Returns (scrubbed_text, redacted_flag).
    """
    redacted = False
    for pat, repl in SECRET_PATTERNS:
        new_text, n = pat.subn(repl, text)
        if n:
            redacted = True
            text = new_text
    return text, redacted


def walk_files(root: Path):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        # filter out excluded dirs in-place so walk won't descend
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            p = Path(dirpath) / fn
            # Skip snapshot output itself
            if p.resolve() == OUT.resolve():
                continue
            files.append(p)
    return sorted(files)


def build_tree_section(files, root: Path) -> str:
    tree = []
    # Build a set of directories to show
    dirs = set()
    for f in files:
        dirs.add(str(f.parent.relative_to(root)))
    # Print a simple top-level tree (only one level deep for readability)
    tree.append("## Folder tree\n")
    tree.append("- ./")
    # list root files (hide obvious binary files)
    root_files = [f.name for f in files if f.parent == root and not is_binary_path(f)]
    for rf in sorted(root_files):
        tree.append(f"  - {rf}")
    # list top-level directories (exclude files at repo root)
    top_dirs = sorted({p.parts[0] for p in {f.relative_to(root) for f in files} if len(p.parts) > 1})
    for d in top_dirs:
        if d == '.':
            continue
        tree.append(f"  - {d}/")
    tree.append("\n---\n")
    return "\n".join(tree)


def summarize_package_lock(p: Path) -> str:
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return "Could not parse package-lock.json; omitted."
    deps = data.get("dependencies") or {}
    top = []
    for name, info in deps.items():
        ver = info.get("version") if isinstance(info, dict) else str(info)
        top.append(f"- {name}: {ver}")
        if len(top) >= 40:
            break
    total = len(deps)
    return f"package-lock.json summary: top-level dependencies ({min(40, total)}) of {total}:\n" + "\n".join(top)


def should_skip_content(p: Path) -> bool:
    if p.name in SKIP_FILES:
        return True
    if is_binary_path(p):
        return True
    try:
        size = p.stat().st_size
        if size > MAX_BYTES:
            return True
    except Exception:
        return True
    return False


def read_text_head(p: Path, max_lines=MAX_LINES) -> tuple[str, bool]:
    """Return (text, truncated_flag)"""
    try:
        with p.open("r", encoding='utf-8', errors='replace') as fh:
            lines = []
            for i, line in enumerate(fh):
                if i >= max_lines:
                    return ("".join(lines), True)
                lines.append(line)
            return ("".join(lines), False)
    except Exception as e:
        return (f"[Could not read file: {e}]\n", False)


def main():
    files = walk_files(ROOT)
    with OUT.open("w", encoding='utf-8') as out:
        out.write(f"# Project snapshot: {ROOT.name}\n\n")
        out.write(f"_Generated: {datetime.now(timezone.utc).isoformat()}\n\n")
        out.write(build_tree_section(files, ROOT))

        for f in files:
            # Skip most CRA public assets except minimal HTML/manifest
            try:
                if f.is_relative_to(PUBLIC_DIR) and f.name not in PUBLIC_INCLUDE_ONLY:
                    continue
            except AttributeError:
                # Python < 3.9 fallback
                if str(PUBLIC_DIR) in str(f.parent) and f.name not in PUBLIC_INCLUDE_ONLY:
                    continue

            rel = f.relative_to(ROOT)
            # Skip overly verbose aggregate docs that don't add signal
            if rel.as_posix() == "docs/FullContext.md":
                continue
            # Special case: lockfiles -> summary/omit
            if f.name == "package-lock.json":
                out.write(f"## ./{rel}\n```\n")
                out.write(summarize_package_lock(f) + "\n```")
                out.write("\n\n")
                continue
            if f.name in {"yarn.lock", "pnpm-lock.yaml"}:
                # omit lockfile content entirely
                continue
            # Skip binary by extension or content sniff
            if is_binary_path(f) or looks_binary_file(f):
                continue
            try:
                size = f.stat().st_size
            except Exception:
                size = 0
            # quick peek for sensitivity (read a tiny head)
            sample_text = ""
            if size <= MAX_BYTES:
                try:
                    with f.open("r", encoding='utf-8', errors='replace') as fh:
                        sample_text = fh.read(2048)
                except Exception:
                    sample_text = ""
            if is_sensitive_file(f, sample_text):
                out.write(f"## ./{rel}\n```\n[sensitive content omitted]\n```\n\n")
                continue
            if size > MAX_BYTES:
                text, truncated = read_text_head(f, MAX_LINES)
                text, _ = scrub_secrets(text)
                out.write(f"## ./{rel}\n```\n" + text)
                out.write("\n... (truncated)\n```")
                out.write("\n\n")
                continue
            # Small text file -> include full or truncated by lines
            text, truncated = read_text_head(f, MAX_LINES)
            text, red = scrub_secrets(text)
            out.write(f"## ./{rel}\n```\n" + text)
            if truncated:
                out.write("\n... (truncated)")
            out.write("\n```\n\n")

    print(f"Snapshot written to: {OUT}")


if __name__ == '__main__':
    main()
