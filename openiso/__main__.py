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
    from PyQt6.QtWidgets import QApplication
    from openiso.view.window import SkeyEditor

    app = QApplication(sys.argv)
    app.setApplicationName('OpenIso')
    app.setOrganizationName('io.github.rompik')
    app.setOrganizationDomain('github.io')

    window = SkeyEditor()
    window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
