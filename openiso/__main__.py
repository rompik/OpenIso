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


def main():
    """Application entry point."""
    from openiso.application import Application

    app = Application()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())
