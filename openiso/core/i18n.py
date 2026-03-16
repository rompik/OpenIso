# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import os
import glob
import subprocess
import gettext
import locale
import json
from typing import Optional
from openiso.core.constants import LOCALEDIR, AVAILABLE_LANGUAGES

# Global translation state
_gettext = None
lang_trans = None
_current_lang = 'en'
_json_trans = {}

def compile_translations():
    """Auto-compile .po to .mo for all available languages."""
    for po_path in glob.glob(os.path.join(LOCALEDIR, '*.po')):
        lang_code = os.path.splitext(os.path.basename(po_path))[0]
        mo_dir = os.path.join(LOCALEDIR, lang_code, 'LC_MESSAGES')
        mo_path = os.path.join(mo_dir, 'openiso.mo')
        os.makedirs(mo_dir, exist_ok=True)
        # Only recompile if .mo is missing or .po is newer
        if not os.path.exists(mo_path) or os.path.getmtime(po_path) > os.path.getmtime(mo_path):
            try:
                subprocess.run([
                    'msgfmt', po_path, '-o', mo_path
                ], check=True)
            except Exception as e:
                print(f"[i18n] Failed to compile {po_path} to {mo_path}: {e}")

def get_translator(lang_code):
    """Set up and return a translator for the given language code."""
    gettext.bindtextdomain('openiso', LOCALEDIR)
    gettext.textdomain('openiso')
    return gettext.translation('openiso', LOCALEDIR, languages=[lang_code], fallback=True)

# Initialize translations
compile_translations()

def get_current_language():
    """Returns the current language code."""
    return _current_lang

def _t(key):
    """Translate using JSON data (supports nested dictionaries) or fallback to gettext."""
    global _json_trans, _gettext

    if not key:
        return key

    # Try nested lookup using dot notation (always lowercase for path components)
    parts = key.split('.')
    curr = _json_trans
    for part in parts:
        # Normalize part to lowercase for key lookup
        p = part.lower()
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        else:
            # Fallback to gettext if path not found in JSON
            if _gettext:
                return _gettext(key)
            return key

    # If we found a result
    if isinstance(curr, str):
        return curr
    elif isinstance(curr, dict) and "_name" in curr:
        # Special case: dictionary node has a display name
        return curr["_name"]

    # If it's still a dict but no _name, return the last part of the key
    if parts:
        return parts[-1]

    if _gettext:
        return _gettext(key)
    return key

def setup_i18n(lang_code=None):
    """Initialize or switch the current translation language."""
    global _gettext, lang_trans, _current_lang, _json_trans

    # If already set and no new code provided, just return current translator
    if lang_code is None and _gettext is not None:
        return _t

    if lang_code is None:
        try:
            language, encoding = locale.getlocale()
            if not language:
                language = os.environ.get('LANG', 'en').split('.')[0]
            lang_code = language.replace('-', '_') if language else 'en'
        except Exception:
            lang_code = 'en'

    # Normalize lang_code to match AVAILABLE_LANGUAGES (e.g., ru_RU -> ru)
    supported_codes = [lang[1] for lang in AVAILABLE_LANGUAGES]
    if lang_code not in supported_codes:
        # Try short code (e.g. 'ru')
        short_code = lang_code.split('_')[0]
        if short_code in supported_codes:
            lang_code = short_code
        else:
            # Try to match any supported code if possible
            for code in supported_codes:
                if code in lang_code:
                    lang_code = code
                    break
            else:
                lang_code = 'en'

    print(f"[i18n] Setting up language: {lang_code}")
    try:
        lang_trans = get_translator(lang_code)
        _gettext = lang_trans.gettext
    except Exception as e:
        print(f"[i18n] Failed to get translator for {lang_code}: {e}")
        _gettext = lambda x: x

    _current_lang = lang_code

    # Load JSON translations
    _json_trans = {}
    json_path = os.path.join(LOCALEDIR, f"{lang_code}.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                _json_trans = json.load(f)
            print(f"[i18n] Loaded JSON translations from {json_path}")
        except Exception as e:
            print(f"[i18n] Failed to load JSON translations from {json_path}: {e}")
    else:
        print(f"[i18n] JSON translation file not found: {json_path}")

    return _t

def save_json_translation(key: str, text: str, lang_code: Optional[str] = None):
    """Saves a translation to the JSON file for the given language (supports nested structure)."""
    global _current_lang, _json_trans
    if lang_code is None:
        lang_code = _current_lang or 'en'

    json_path = os.path.join(LOCALEDIR, f"{lang_code}.json")
    trans_data = {}

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                trans_data = json.load(f)
        except Exception:
            pass

    # Build nested structure
    parts = key.split('.')
    curr = trans_data
    for i, part in enumerate(parts[:-1]):
        if part not in curr or not isinstance(curr[part], dict):
            # If current node is a string and we need to go deeper,
            # preserve the string as _name and convert to dict
            old_val = curr.get(part)
            curr[part] = {}
            if isinstance(old_val, str):
                curr[part]["_name"] = old_val
        curr = curr[part]

    leaf = parts[-1]
    if leaf not in curr or curr[leaf] != text:
        # If the leaf would overwrite a dict, store it as _name instead?
        # But usually keys like skey_name and skey_description are at the end.
        if isinstance(curr.get(leaf), dict):
            curr[leaf]["_name"] = text
        else:
            curr[leaf] = text

        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(trans_data, f, ensure_ascii=False, indent=2)

            # Also update the in-memory global _json_trans if same language
            if lang_code == _current_lang:
                _json_trans = trans_data
        except Exception as e:
            print(f"[i18n] Failed to save JSON translation: {e}")

# Initial setup with system locale
setup_i18n()
