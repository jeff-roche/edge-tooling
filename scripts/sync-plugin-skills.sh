#!/bin/bash
# Sync plugin skills to .claude/skills/ as symlinks.
#
# Traverses plugins/*/skills/*/SKILL.md and creates relative symlinks
# in .claude/skills/ named <plugin-name>-<skill-name>.
#
# Usage: ./scripts/sync-plugin-skills.sh [--execute | --verify]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="${REPO_ROOT}/.claude/skills"

mode="dry-run"
case "${1:-}" in
    --execute) mode="execute" ;;
    --verify)  mode="verify" ;;
esac
[[ "${mode}" == "dry-run" ]] && echo "[DRY-RUN] Use --execute to apply changes, --verify to check consistency"

mkdir -p "${SKILLS_DIR}"

# Remove stale symlinks (pointing to non-existent targets)
while read -r link; do
    if [[ "${mode}" == "verify" ]]; then
        echo "FAIL: stale symlink: $(basename "${link}")"
        exit 1
    fi
    echo "  remove stale: $(basename "${link}")"
    [[ "${mode}" == "execute" ]] && rm -f "${link}"
done < <(find "${SKILLS_DIR}" -maxdepth 1 -type l ! -exec test -e {} \; -print)

# Create symlinks for all plugin skills
created=0
skipped=0
for skill_md in "${REPO_ROOT}"/plugins/*/skills/*/SKILL.md; do
    [[ -f "${skill_md}" ]] || continue

    # Extract plugin and skill names from path
    # plugins/<plugin>/skills/<skill>/SKILL.md
    rel_path="${skill_md#"${REPO_ROOT}"/}"
    plugin_name=$(echo "${rel_path}" | cut -d/ -f2)
    skill_name=$(echo "${rel_path}" | cut -d/ -f4)

    link_name="${plugin_name}-${skill_name}"
    link_path="${SKILLS_DIR}/${link_name}"
    target="../../plugins/${plugin_name}/skills/${skill_name}"

    if [[ -L "${link_path}" ]]; then
        existing=$(readlink "${link_path}")
        if [[ "${existing}" == "${target}" ]]; then
            skipped=$((skipped + 1))
            continue
        fi
        if [[ "${mode}" == "verify" ]]; then
            echo "FAIL: wrong target: ${link_name} (${existing} != ${target})"
            exit 1
        fi
        echo "  update: ${link_name} (was ${existing})"
        [[ "${mode}" == "execute" ]] && rm -f "${link_path}"
    else
        if [[ "${mode}" == "verify" ]]; then
            echo "FAIL: missing symlink: ${link_name}"
            exit 1
        fi
        echo "  create: ${link_name} -> ${target}"
    fi

    [[ "${mode}" == "execute" ]] && ln -s "${target}" "${link_path}"
    created=$((created + 1))
done

echo "Done: ${created} created/updated, ${skipped} unchanged."
