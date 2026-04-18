# Участие в OpenIso

Спасибо за ваш интерес к вкладу в OpenISo! Мы приветствуем участие в различных областях: разработка кода, сообщения об ошибках, предложения и переводы.

## 🚀 Getting Started with Development {#development-getting-started}

### Prerequisites {#development-prerequisites}

Прежде чем приступить к разработке, убедитесь, что установлены следующие компоненты:

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Скачать Git](https://git-scm.com/downloads)
- Редактор кода или IDE (Visual Studio Code, PyCharm, и т. д.)

### Setting Up Your Development Environment {#development-environment}

1. **Клонировать репозиторий**

        ```
         git clone https://github.com/rompik/OpenIso.git
         cd OpenIso
        ```

2. **Создать виртуальную среду (необязательно, но рекомендуется)**

   Linux:

        ```
         python3 -m venv venv
         source venv/bin/activate
        ```

   Windows:

        ```
         python -m venv venv
         venv\Scripts\activate
        ```

3. **Установить зависимости**

        ```
         pip install -r requirements.txt
        ```

### Running the Application {#running-the-application}

Чтобы запустить OpenIso в режиме разработки:

```bash
python -m openiso
```

Или если вы находитесь в корневом каталоге проекта:

```bash
python openiso/__main__.py
```

### Project Structure {#project-structure}

```
OpenIso/
<unk> <unk> <unk> -openiso/
<unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> -контроллер/# логика и обработка данных
<unk> <unk> <unk> <unk> <unk> <unk> -ядро/# основных утилит (константы, парсер, i18n)
<unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> моделей данных (геометрия, ключ, перечисления)
<unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> <unk> Vie/ # компонентов интерфейса и окон
<unk> <unk> <unk> <unk> <unk> -данные/ # Ресурсы (значки, значки, таблицы стилей, скрипты базы данных)
<unk> <unk> -docs/# Документация на нескольких языках
<unk> <unk> <unk> <unk> po/ # Файлы перевода (rowdin)
<unk> <unk> <unk> <unk> <unk> <unk> <unk> Требования. xt # зависимости Python
```

### Development Workflow {#development-workflow}

1.

        ```
         git checkout -b feature/your-feature-name
        ```

2. **Make Your Changes**

   - Follow the existing code style and structure
   - Add comments for complex logic
   - Test your changes thoroughly

3. **Commit Your Work**

        ```
         git commit -m "Describe your changes clearly"
        ```

4. **Push and Create a Pull Request**

        ```
         git push origin feature/your-feature-name
        ```

   Then create a Pull Request on GitHub for review.

## � Coding Standards {#coding-standards}

We follow standard Python conventions to maintain code quality.

- **PEP 8:** Follow standard Python style guide (4 spaces indentation, snake_case for functions/variables, CamelCase for classes).

- **Docstrings:** All public functions, classes, and modules should have docstrings explaining their purpose, arguments, and return values.

        ```
        def load_skey(self, skey_id: int) -> SkeyData:
            """
            Loads a symbol definition from the database.
        
            Args:
                skey_id (int): The unique identifier of the symbol.
        
            Returns:
                SkeyData: An object containing symbol properties.
            """
        ```

- **Type Hints:** Use type annotations (`typing`) for function signatures to improve clarity and IDE support.

- **Testing:** Add unit tests for new logic (currently in `tests/`). Run tests before submitting a PR.

## 📝 Translation Contributions {#translation-contributions}

We support multiple languages (English, Russian) and welcome new translations.

### Adding a New Language {#adding-a-new-language}

1. Add the language code (e.g., `de`, `es`) to `po/LINGUAS`.

2. Run the update script:

        ```
         ./scripts/localisation/update_translations.sh
        ```

3. Edit the newly created `.po` file in `po/` (e.g., `po/de.po`) using Poedit or a text editor.

4. Commit the `.po` file.

See [Localization Guide](./LOCALISATION.md) for more details.

---

[Return to Index](./INDEX.MD)

1. Visit our [project page on Crowdin](https://crowdin.com/project/openiso).
2. Select a language you are proficient in.
3. Start translating the available strings. You can also vote on translations provided by other contributors.
4. Once translations are ready, they will be automatically submitted to this repository via a Pull Request.

**Note:** Please do not submit translation Pull Requests directly on GitHub. All text changes should be handled through Crowdin to prevent synchronization conflicts.

## 🐛 Reporting Issues {#reporting-issues}

If you found a bug or have a feature request:

1. Check [existing issues](https://github.com/rompik/OpenIso/issues) to avoid duplicates
2. Create a new issue with a clear description
3. Include steps to reproduce (for bugs)
4. Attach screenshots or files if relevant

## 📋 Code Guidelines {#code-guidelines}

- Write clean, readable code
- Use type hints where applicable
- Comment complex algorithms and business logic
- Follow PEP 8 naming conventions
- Test your changes before submitting a PR

## 💡 Need Help? {#need-help}

- Check the [Documentation](https://github.com/rompik/OpenIso/tree/main/docs)
- Review existing issues and discussions
- Feel free to ask questions in Pull Request discussions

---

Thank you for helping make OpenIso better!
