# OpenIso Documentation

Welcome to the documentation for **OpenIso**. This guide covers installation, usage, symbol creation, database architecture, and contribution guidelines.

## 📚 Table of Contents

### 🚀 Getting Started
*   [**OpenIso Overview**](./INTRO.MD) — Overview of OpenIso, its purpose, and key features.
*   [Purpose](./INTRO.MD#purpose)
*   [Key Features](./INTRO.MD#key-features)
*   [Vector Editing](./INTRO.MD#vector-editing)
*   [Connection Management](./INTRO.MD#connection-management)
*   [Format Support](./INTRO.MD#format-support)
*   [Cross-Platform](./INTRO.MD#cross-platform)
*   [**Installation Guide**](./INSTALL.MD) — System requirements and installation instructions for Linux and Windows.
*   [System Requirements](./INSTALL.MD#system-requirements)
*   [Running from Source](./INSTALL.MD#running-from-source)
*   [Prerequisites](./INSTALL.MD#prerequisites)
*   [Step-by-Step Setup](./INSTALL.MD#step-by-step)
*   [Building Standalone Application](./INSTALL.MD#building-standalone-application)
*   [Windows Executable](./INSTALL.MD#windows-executable)
*   [Linux Flatpak](./INSTALL.MD#linux-flatpak)

### 🛠️ User Guide
*   [**User Guide**](./USAGE.MD) — Overview of the interface and core editing workflow.
*   [The Interface](./USAGE.MD#the-interface)
*   [Detailed Operations](./USAGE.MD#detailed-operations)
*   [Navigating Symbols](./USAGE.MD#navigating-symbols)
*   [Editing Geometry](./USAGE.MD#editing-geometry)
*   [Understanding Connections](./USAGE.MD#understanding-connections)
*   [Saving Changes](./USAGE.MD#saving-changes)
*   [**Creating Symbols**](./CREATING_SYMBOL.MD) — Step-by-step tutorial for creating isometric symbols (SKEYs).
*   [Tool Location](./CREATING_SYMBOL.MD#tool-location)
*   [Gate Valve Tutorial](./CREATING_SYMBOL.MD#step-by-step-gate-valve)
*   [Step 1: Preparing a New SKEY](./CREATING_SYMBOL.MD#step-1-prepare-skey)
*   [Step 2: Drawing the Symbol Body](./CREATING_SYMBOL.MD#step-2-draw-body)
*   [Step 3: Adding Connection Points](./CREATING_SYMBOL.MD#step-3-connections)
*   [Step 4: Adding a Spindle Point](./CREATING_SYMBOL.MD#step-4-spindle)
*   [Step 5: Saving](./CREATING_SYMBOL.MD#step-5-saving)
*   [Tips](./CREATING_SYMBOL.MD#tips)
*   [**Reference Guide**](./SYMBOLS.MD) — Comprehensive reference for primitives, connection types, and symbol keys.
*   [Basic Primitives](./SYMBOLS.MD#basic-primitives)
*   [Connection Types](./SYMBOLS.MD#connection-types)
*   [Spindle Handles](./SYMBOLS.MD#spindle-handles)
*   [Symbol Catalog](./SYMBOLS.MD#symbol-catalog)
*   [Symbol Anatomy](./SYMBOLS.MD#symbol-anatomy)
*   [Connection Points](./SYMBOLS.MD#connection-points)
*   [Geometry Elements](./SYMBOLS.MD#geometry-elements)
*   [Properties](./SYMBOLS.MD#properties)
*   [**Terminal Commands**](./TERMINAL.MD) — Reference for the built-in command-line interface.
*   [Move Command](./TERMINAL.MD#move)
*   [Rotate Command](./TERMINAL.MD#rotate)
*   [Clear Command](./TERMINAL.MD#clear)
*   [Help Command](./TERMINAL.MD#help)

### 🔧 Architecture & Data
*   [**Database Structure**](./DATABASE.MD) — Deep dive into the SQLite storage schema, versioning, and data models.
*   [Database Schema](./DATABASE.MD#database-schema)
*   [skeys Table](./DATABASE.MD#skeys-table)
*   [geometry Table](./DATABASE.MD#geometry-table)
*   [transactions Table](./DATABASE.MD#transactions-table)
*   [spindles Table](./DATABASE.MD#spindles-table)
*   [Data Flow](./DATABASE.MD#data-flow)

### 🤝 Contributing
*   [**Contribution Guide**](./CONTRIBUTING.MD) — How to set up a dev environment, coding standards, and workflow.
*   [Development Getting Started](./CONTRIBUTING.MD#development-getting-started)
*   [Development Prerequisites](./CONTRIBUTING.MD#development-prerequisites)
*   [Development Environment](./CONTRIBUTING.MD#development-environment)
*   [Running the Application](./CONTRIBUTING.MD#running-the-application)
*   [Project Structure](./CONTRIBUTING.MD#project-structure)
*   [Development Workflow](./CONTRIBUTING.MD#development-workflow)
*   [Coding Standards](./CONTRIBUTING.MD#coding-standards)
*   [Translation Contributions](./CONTRIBUTING.MD#translation-contributions)
*   [Adding a New Language](./CONTRIBUTING.MD#adding-a-new-language)
*   [Reporting Issues](./CONTRIBUTING.MD#reporting-issues)
*   [Code Guidelines](./CONTRIBUTING.MD#code-guidelines)
*   [Need Help](./CONTRIBUTING.MD#need-help)
*   [**Localization**](./LOCALISATION.md) — Instructions for translating the application.
*   [update_translations.sh](./LOCALISATION.md#update-translations-sh)
*   [What it does](./LOCALISATION.md#what-it-does)
*   [Requirements](./LOCALISATION.md#requirements)
*   [Usage](./LOCALISATION.md#usage)
*   [Workflow](./LOCALISATION.md#workflow)
*   [Adding a New Language](./LOCALISATION.md#adding-language)
*   [File Structure](./LOCALISATION.md#file-structure)
*   [Translation Tools](./LOCALISATION.md#translation-tools)
*   [Troubleshooting](./LOCALISATION.md#troubleshooting)
*   [JSON Translations](./LOCALISATION.md#json-translations)

---
*OpenIso Project &copy; 2024 Roman Parygin. Licensed under MIT.*

