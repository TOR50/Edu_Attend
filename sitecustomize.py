"""Project-level interpreter patches and safeguards."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path


def _patch_importlib_from_fallback() -> None:
    """Populate missing attributes in the stdlib importlib module.

    The user's system Python 3.13 installation ships an empty
    ``importlib.__init__`` which omits ``import_module`` and related helpers
    required by Django. We hydrate the module using a fallback copy that ships
    with the MSYS2 Python 3.12 runtime available on this machine.
    """

    src_candidates = (
        Path("C:/Users/rauha/AppData/Local/Programs/Python/Python313/Lib/importlib/__init__.py"),
        Path("C:/msys64/ucrt64/lib/python3.12/importlib/__init__.py"),
    )

    for candidate in src_candidates:
        try:
            text = candidate.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        if text.strip():
            importlib_dict = importlib.__dict__
            exec(compile(text, str(candidate), "exec"), importlib_dict)
            # Ensure attribute lookups see the freshly populated dictionary.
            sys.modules["importlib"] = importlib
            return

    raise RuntimeError("Unable to patch importlib; no fallback source found.")


if not hasattr(importlib, "import_module"):
    _patch_importlib_from_fallback()
