# Installation Guide

This guide covers how to install and run OpenIso.

## System Requirements {#system-requirements}

- **Linux:** Ubuntu 22.04+, Fedora 38+, Arch Linux.
- **Windows:** Windows 10 or 11 (64-bit).
- **Python:** 3.10 to 3.12 (For building from source).
- **Dependencies:** PyQt6 >= 6.0.0, markdown >= 3.0.0, pyinstaller >= 5.0.0 (for building).

---

## 🚀 Running from Source {#running-from-source}

If you want to contribute or modify the code, running from source is recommended.

### Prerequisites {#prerequisites}

| System | Pre-Req Command (Debian/Ubuntu) | Pre-Req Command (Windows) |
|---|---|---|
| Basics | `sudo apt install python3 python3-venv git` | [Download Python](https://www.python.org/downloads/) |

### Step-by-Step {#step-by-step}

1. **Clone the Repository**

        git clone https://github.com/rompik/OpenIso.git
        cd OpenIso

2. **Create a Virtual Environment**

   It's highly recommended to use a virtual environment to avoid conflicts with system packages.

   Linux/macOS:

        python3 -m venv venv
        source venv/bin/activate

   Windows:

        python -m venv venv
        .\venv\Scripts\activate

3. **Install Dependencies**

        pip install -r requirements.txt

4. **Run the Application**

        python -m openiso

---

## 📦 Building Standalone Application {#building-standalone-application}

If you prefer a single executable file:

### Windows Executable {#windows-executable}
Use PyInstaller with the provided spec file:
```bash
pyinstaller --clean OpenIso_win.spec
```
The resulting `.exe` will be located in the `dist/` folder.

### Linux Flatpak {#linux-flatpak}
For Linux users, a Flatpak build system is available. Refer to the `io.github.rompik.OpenIso.desktop.in` and `meson.build` files for packaging details.

---
[Return to Index](./INDEX.MD)

