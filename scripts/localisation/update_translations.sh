#!/bin/bash

# Update Translations - Extract, merge, and compile

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts/localisation"
PO_DIR="$PROJECT_ROOT/po"
BACKUP_DIR="$PO_DIR/.backup"

echo "🌍 OpenIso Translation Update"
echo "============================="
echo ""

# Step 1: Create backup
echo "📦 Creating backup..."
mkdir -p "$BACKUP_DIR"
cp "$PO_DIR/messages.pot" "$BACKUP_DIR/messages.pot.bak" 2>/dev/null || true
for po_file in "$PO_DIR"/*.po; do
    [ -f "$po_file" ] && cp "$po_file" "$BACKUP_DIR/$(basename "$po_file").bak"
done
echo "✅ Backup created in $BACKUP_DIR"
echo ""

# Step 2: Extract all translatable strings
echo "📝 Extracting translatable strings from all Python files..."
cd "$PROJECT_ROOT"

required_commands=(find sort xgettext msgmerge msgfmt awk grep sed diff head cut du)
for cmd in "${required_commands[@]}"; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "❌ Required command not found: $cmd"
        exit 1
    fi
done

mapfile -t PYTHON_FILES < <(find openiso -type f -name "*.py" | sort)

if [ "${#PYTHON_FILES[@]}" -eq 0 ]; then
    echo "❌ No Python files found under openiso/"
    exit 1
fi

echo "🔍 Found files:"
for file in "${PYTHON_FILES[@]}"; do
    echo "   • $file"
done
echo ""

xgettext \
    --language=Python \
    --keyword=_:1 \
    --keyword=_t:1 \
    --keyword=ngettext:1,2 \
    --output="$PO_DIR/messages.pot" \
    --from-code=UTF-8 \
    --add-comments=Translators \
    --copyright-holder="OpenIso Contributors" \
    "${PYTHON_FILES[@]}"

TOTAL_STRINGS=$(grep -c "^msgid \"" "$PO_DIR/messages.pot" || echo "0")
echo "✅ Extracted $TOTAL_STRINGS total strings to messages.pot"
echo ""

# Step 3: Identify new strings
echo "🔎 Identifying NEW strings..."

NEW_STRINGS_FILE="$PROJECT_ROOT/po/NEW_STRINGS_FOR_TRANSLATION.txt"
> "$NEW_STRINGS_FILE"

if [ -f "$BACKUP_DIR/messages.pot.bak" ]; then
    NEW_COUNT=$(diff <(grep "^msgid \"" "$BACKUP_DIR/messages.pot.bak" 2>/dev/null | sort) \
                     <(grep "^msgid \"" "$PO_DIR/messages.pot" | sort) \
                     | grep "^>" | wc -l | tr -d ' \t\n')

    if [ "${NEW_COUNT:-0}" -gt 0 ]; then
        diff <(grep "^msgid \"" "$BACKUP_DIR/messages.pot.bak" 2>/dev/null | sort) \
             <(grep "^msgid \"" "$PO_DIR/messages.pot" | sort) \
             | grep "^>" | sed 's/^> msgid "//' | sed 's/"$//' >> "$NEW_STRINGS_FILE"
        echo "✅ Found $NEW_COUNT new strings"
    else
        echo "✅ No new strings (all already translated)"
    fi
else
    echo "⚠️  No previous backup. Treating all as new baseline."
fi
echo ""

# Step 4: Update .po files with new strings
echo "🔄 Updating .po files..."
echo ""

LANGUAGE_STATS=""

for po_file in "$PO_DIR"/*.po; do
    if [ -f "$po_file" ]; then
        lang=$(basename "$po_file" .po)
        echo "   📍 Merging $lang.po..."

        msgmerge --update --backup=off "$po_file" "$PO_DIR/messages.pot"

        # Calculate statistics
        total=$(grep -c "^msgid \"" "$po_file" 2>/dev/null | tr -d ' \t\n' || echo "0")
        translated=$(grep "^msgstr \"" "$po_file" 2>/dev/null | grep -v "^msgstr \"\"" | wc -l | tr -d ' \t\n')
        fuzzy=$(grep -c "^#, fuzzy" "$po_file" 2>/dev/null | tr -d ' \t\n' || echo "0")
        untranslated=$(( ${total:-0} - ${translated:-0} - ${fuzzy:-0} ))

        LANGUAGE_STATS="$LANGUAGE_STATS
   $lang: $translated/$total translated, $fuzzy fuzzy, $untranslated new"

        printf "      ✓ %3d/%3d translated, %3d fuzzy, %3d new\n" \
            "${translated:-0}" "${total:-0}" "${fuzzy:-0}" "${untranslated:-0}"
    fi
done

echo ""

# Step 5: Show fuzzy strings that need translation
echo "🔴 Fuzzy Strings (Need Translation):"
echo "===================================="
echo ""

HAS_FUZZY=false

for po_file in "$PO_DIR"/*.po; do
    if [ -f "$po_file" ]; then
        lang=$(basename "$po_file" .po)
        fuzzy_count=$(grep -c "^#, fuzzy" "$po_file" 2>/dev/null || echo "0")
        fuzzy_count=$(echo "$fuzzy_count" | tr -d ' \t\n')

        if [ "$fuzzy_count" -gt 0 ]; then
            HAS_FUZZY=true
            echo "📍 $lang.po - $fuzzy_count fuzzy strings:"

            awk '
                /^#, fuzzy/ {
                    getline
                    if ($0 ~ /^msgid/) {
                        msgid = $0
                        sub(/^msgid "/, "", msgid)
                        sub(/"$/, "", msgid)
                        printf "   • %s\n", msgid
                    }
                }
            ' "$po_file" | head -5

            remaining=$((fuzzy_count - 5))
            if [ "$remaining" -gt 0 ]; then
                echo "   ... and $remaining more"
            fi
            echo ""
        fi
    fi
done

if [ "$HAS_FUZZY" = false ]; then
    echo "✅ No fuzzy strings - all translations up to date!"
    echo ""
fi

# Step 6: Compile translations to .mo files
echo "🔨 Compiling translations..."
echo ""

for po_file in "$PO_DIR"/*.po; do
    if [ -f "$po_file" ]; then
        lang=$(basename "$po_file" .po)
        mo_dir="$PO_DIR/$lang/LC_MESSAGES"
        mkdir -p "$mo_dir"

        msgfmt -o "$mo_dir/openiso.mo" "$po_file"
        mo_size=$(du -h "$mo_dir/openiso.mo" | cut -f1)
        echo "   ✅ $lang: $mo_dir/openiso.mo ($mo_size)"
    fi
done

echo ""
echo "═════════════════════════════════════════"
echo "✅ Translation Update Complete"
echo "═════════════════════════════════════════"
echo ""
echo "📊 Summary:$LANGUAGE_STATS"
echo ""

if [ -f "$NEW_STRINGS_FILE" ] && [ -s "$NEW_STRINGS_FILE" ]; then
    echo "📋 New strings saved to: NEW_STRINGS_FOR_TRANSLATION.txt"
    echo ""
fi

echo "📌 Next Steps:"
if [ "$HAS_FUZZY" = true ]; then
    echo "   1. Edit .po files to translate fuzzy strings"
    echo "   2. Remove '#, fuzzy' comment when translation is complete"
    echo "   3. Run this script again to recompile"
    echo "   4. Test: LANG=ru_RU python -m openiso"
else
    echo "   1. Commit changes: git add po/ && git commit -m 'Update translations'"
    echo "   2. Test: LANG=ru_RU python -m openiso"
fi
echo ""
echo "🌐 Crowdin Integration:"
echo "   crowdin upload sources"
echo "   crowdin download"
echo ""