# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 OpenIso Roman PARYGIN

import gettext
import glob
import json
import locale
import logging
import os
import subprocess
from typing import Optional

from openiso.core.constants import AVAILABLE_LANGUAGES, LOCALEDIR


logger = logging.getLogger(__name__)


def _identity(text: str) -> str:
    return text


# Runtime translation state shared across module functions.
_state = {
    "gettext": None,
    "translator": None,
    "current_lang": "en",
    "json_trans": {},
}

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
            except (subprocess.CalledProcessError, OSError) as err:
                logger.warning("[i18n] Failed to compile %s to %s: %s", po_path, mo_path, err)

def get_translator(lang_code):
    """Set up and return a translator for the given language code."""
    gettext.bindtextdomain('openiso', LOCALEDIR)
    gettext.textdomain('openiso')
    return gettext.translation('openiso', LOCALEDIR, languages=[lang_code], fallback=True)

# Initialize translations
compile_translations()

def get_current_language():
    """Returns the current language code."""
    return _state["current_lang"]

def _t(key):
    """Translate using JSON data (supports nested dictionaries) or fallback to gettext."""
    if not key:
        return key

    # Try nested lookup using dot notation (always lowercase for path components)
    parts = key.split('.')
    curr = _state["json_trans"]
    for part in parts:
        # Normalize part to lowercase for key lookup
        p = part.lower()
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        else:
            # Fallback to gettext if path not found in JSON
            gettext_fn = _state["gettext"]
            if gettext_fn:
                return gettext_fn(key)
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

    gettext_fn = _state["gettext"]
    if gettext_fn:
        return gettext_fn(key)
    return key

def setup_i18n(lang_code=None):
    """Initialize or switch the current translation language."""
    # If already set and no new code provided, just return current translator
    if lang_code is None and _state["gettext"] is not None:
        return _t

    if lang_code is None:
        try:
            language, _encoding = locale.getlocale()
            if not language:
                language = os.environ.get('LANG', 'en').split('.')[0]
            lang_code = language.replace('-', '_') if language else 'en'
        except (locale.Error, ValueError, TypeError):
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

    logger.info("[i18n] Setting up language: %s", lang_code)
    try:
        translator = get_translator(lang_code)
        _state["translator"] = translator
        _state["gettext"] = translator.gettext
    except OSError as err:
        logger.warning("[i18n] Failed to get translator for %s: %s", lang_code, err)
        _state["translator"] = None
        _state["gettext"] = _identity

    _state["current_lang"] = lang_code

    # Load JSON translations
    _state["json_trans"] = {}
    json_path = os.path.join(LOCALEDIR, f"{lang_code}.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                _state["json_trans"] = json.load(f)
            logger.debug("[i18n] Loaded JSON translations from %s", json_path)
        except (OSError, json.JSONDecodeError) as err:
            logger.warning("[i18n] Failed to load JSON translations from %s: %s", json_path, err)
    else:
        logger.debug("[i18n] JSON translation file not found: %s", json_path)

    return _t

def save_json_translation(key: str, text: str, lang_code: Optional[str] = None):
    """Saves a translation to the JSON file for the given language (supports nested structure)."""
    if lang_code is None:
        lang_code = _state["current_lang"] or 'en'

    json_path = os.path.join(LOCALEDIR, f"{lang_code}.json")
    trans_data = {}

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                trans_data = json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

    # Build nested structure
    parts = key.split('.')
    curr = trans_data
    for part in parts[:-1]:
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

            # Keep in-memory translations in sync for the active language.
            if lang_code == _state["current_lang"]:
                _state["json_trans"] = trans_data
        except (OSError, TypeError, ValueError) as err:
            logger.warning("[i18n] Failed to save JSON translation: %s", err)

# Initial setup with system locale
setup_i18n()
