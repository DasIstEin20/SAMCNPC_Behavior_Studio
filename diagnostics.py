"""Local diagnostics for startup/callback exceptions (no network, no dependencies)."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys


def log_exception(detail: str, root=None) -> Path | None:
    """Append bounded traceback + runtime versions, returning the real log path.

    File output is best-effort, including read-only/home-less installations.
    No project JSON, inventory data or user environment values are collected.
    """
    version = 'unknown'
    if root is not None:
        try:
            version = str(root.tk.call('package', 'provide', 'Tk'))
        except Exception:
            pass
    entry = (f'\n--- Behavior Studio 1.2.0 | {datetime.now(timezone.utc).isoformat()} ---\n'
             f'Python {platform.python_version()} | platform {sys.platform} | Tk {version}\n'
             f'{detail[-16000:]}\n')
    try:
        print(entry, file=sys.stderr)
    except (OSError, AttributeError):
        pass
    try:
        path = Path.home() / 'samcnpc-studio-error.log'
        # Rotate one previous log rather than growing it indefinitely.
        if path.exists() and path.stat().st_size > 1_000_000:
            path.replace(path.with_suffix('.log.previous'))
        with path.open('a', encoding='utf-8') as handle:
            handle.write(entry)
        return path
    except (OSError, RuntimeError):
        return None
