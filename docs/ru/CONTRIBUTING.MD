# Contributing to OpenIso

Thank you for your interest in contributing to OpenIso! We welcome contributions in multiple areas: code development, bug reports, feature suggestions, and translations.

## 🚀 Getting Started with Development

### Prerequisites

Before you start developing, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- A code editor or IDE (Visual Studio Code, PyCharm, etc.)

### Setting Up Your Development Environment

1. **Clone the Repository**

   ```bash
   git clone https://github.com/rompik/OpenIso.git
   cd OpenIso
   ```

2. **Create a Virtual Environment (Optional but Recommended)**
   # On Linux
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   # On Windows
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To run OpenIso in development mode:

```bash
python -m openiso
```

Or if you're in the project root directory:

```bash
python openiso/__main__.py
```

### Project Structure

```
OpenIso/
├── openiso/
│   ├── controller/      # Business logic and data handling
│   ├── core/           # Core utilities (constants, parser, i18n)
│   ├── model/          # Data models (geometry, skey, enums)
│   └── view/           # UI components and windows
├── data/               # Resources (icons, stylesheets, database scripts)
├── docs/               # Documentation in multiple languages
├── po/                 # Translation files (Crowdin)
└── requirements.txt    # Python dependencies
```

### Development Workflow

1. **Create a Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow the existing code style and structure
   - Add comments for complex logic
   - Test your changes thoroughly

3. **Commit Your Work**
   ```bash
   git commit -m "Describe your changes clearly"
   ```

4. **Push and Create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub for review.

## 📝 Translation Contributions

Мы используем Crowdin для перевода нашей документации. Это помогает нам держать переводы в актуальном состоянии без необходимости редактировать код напрямую.

How to contribute translations:

1. Visit our [project page on Crowdin](https://crowdin.com/project/openiso).
2. Select a language you are proficient in.
3. Start translating the available strings. You can also vote on translations provided by other contributors.
4. Once translations are ready, they will be automatically submitted to this repository via a Pull Request.

**Note:** Please do not submit translation Pull Requests directly on GitHub. All text changes should be handled through Crowdin to prevent synchronization conflicts.

## 🐛 Reporting Issues

If you found a bug or have a feature request:

1. Check [existing issues](https://github.com/rompik/OpenIso/issues) to avoid duplicates
2. Create a new issue with a clear description
3. Include steps to reproduce (for bugs)
4. Attach screenshots or files if relevant

## 📋 Code Guidelines

- Write clean, readable code
- Use type hints where applicable
- Comment complex algorithms and business logic
- Follow PEP 8 naming conventions
- Test your changes before submitting a PR

## 💡 Need Help?

- Check the [Documentation](https://github.com/rompik/OpenIso/tree/main/docs)
- Review existing issues and discussions
- Feel free to ask questions in Pull Request discussions

---

Thank you for helping make OpenIso better!
