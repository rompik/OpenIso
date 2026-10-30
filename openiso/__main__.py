#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

"""
Main entry point for running openiso as a module.

Usage:
    python -m openiso
"""

import sys
from pathlib import Path


def _ensure_project_root():
    """Prefer this checkout over any separately installed openiso package."""
    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root in sys.path:
        sys.path.remove(project_root)
    sys.path.insert(0, project_root)


def main():
    """Application entry point."""
    _ensure_project_root()
    from openiso.application import Application

    app = Application()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())
