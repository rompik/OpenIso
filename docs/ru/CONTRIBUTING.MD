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
├── po/                 # Переводы интерфейса (GNU gettext)
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

Переводы хранятся в этом GitHub-репозитории и принимаются через pull request. Русский язык является исходным для новых и обновляемых пользовательских руководств.

### Перевод документации

1. Создайте или обновите соответствующую страницу на русском языке в `docs/ru/`.
2. Для другого языка переведите страницу из `docs/ru/` в соответствующую папку `docs/<код-языка>/`.
3. Сохраните ссылки, примеры кода и технические идентификаторы без изменений.
4. Добавьте страницу в языковой `index.json` и откройте pull request.

Если русский оригинал изменился, проверьте соответствующий перевод и обновите его в том же или отдельном pull request. Не добавляйте в индекс ссылку на отсутствующую страницу.

### Перевод интерфейса приложения

Каталоги GNU gettext находятся в `po/`. Чтобы обновить или добавить перевод:

1. Укажите язык в `po/LINGUAS`.
2. Запустите `scripts/localisation/update_translations.sh`.
3. Переведите соответствующий `.po`-файл, повторно запустите скрипт и проверьте приложение.
4. Отправьте изменения через pull request.

См. [руководство по локализации](./LOCALISATION.md). Не переводите идентификаторы кода, имена файлов и значения, которые приложение использует как ключи.

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
