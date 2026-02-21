# Localization Scripts

This directory contains scripts for managing translations in OpenIso.

## update_translations.sh

Automated script to update all localization files.

### What it does:

1. **Extracts translatable strings** from source code to `messages.pot`
2. **Updates .po files** for all languages listed in LINGUAS
3. **Compiles .po to .mo** files for runtime use
4. **Shows translation statistics** for each language

### Requirements:

The script requires GNU gettext tools:

```bash
# On Ubuntu/Debian:
sudo apt install gettext

# On Fedora/RHEL:
sudo dnf install gettext

# On Arch:
sudo pacman -S gettext

# On macOS:
brew install gettext
```

### Usage:

```bash
# Run from anywhere in the project:
./scripts/localisation/update_translations.sh

# Or from the scripts/localisation directory:
cd scripts/localisation
./update_translations.sh
```

### Workflow:

1. **Developer adds translatable strings** in code using `_()` or `_t()`
2. **Run the script** to extract new strings and update .po files
3. **Translators edit .po files** using poedit or text editor
4. **Run the script again** to compile updated translations
5. **Test in application** to verify translations

### Adding a new language:

1. Add the language code to `po/LINGUAS` file:
   ```
   ru
   fr
   zh_CN
   de    # <- new language
   ```

2. Run the update script:
   ```bash
   ./scripts/localisation/update_translations.sh
   ```

3. The script will automatically create `po/de.po`

4. Edit `po/de.po` to add translations

5. Run the script again to compile

### File structure:

- `po/POTFILES.in` - List of source files with translatable strings
- `po/LINGUAS` - List of available language codes
- `po/messages.pot` - Template file with all translatable strings
- `po/{lang}.po` - Translation files for each language
- `po/{lang}.mo` - Compiled binary translation files
- `po/{lang}/LC_MESSAGES/openiso.mo` - Standard gettext location

### Translation tools:

- **Poedit** - https://poedit.net/ (Recommended GUI editor)
- **Lokalize** - KDE translation tool
- **Gtranslator** - GNOME translation tool
- **Text editor** - Any editor can edit .po files

### Troubleshooting:

**"command not found: xgettext"**

- Install gettext package (see Requirements above)

**"No source files found in POTFILES.in"**

- Check that `po/POTFILES.in` exists and contains file paths

**"Failed to compile .mo"**

- Check for syntax errors in .po file
- Run `msgfmt -c po/{lang}.po` to validate

### JSON translations:

The project also uses JSON files (`po/en.json`, `po/ru.json`) for structured translations. These need to be updated manually if used.
