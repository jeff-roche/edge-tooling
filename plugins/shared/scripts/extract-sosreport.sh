#!/usr/bin/bash
set -euo pipefail

# Extract sosreport archives from downloaded Prow job artifacts and write
# a JSON index of the high-signal files inside them.
#
# Usage:
#   extract-sosreport.sh <top-dir>
#
#   <top-dir>: root directory to search recursively for sosreport-*.tar.xz.
#              Tarballs are grouped by parent directory; each group is
#              extracted into <parent-dir>/sos-extracted/ with its own
#              index.json.
#
# Output: writes <parent-dir>/sos-extracted/index.json per directory:
#   {"sosreports": [{
#      "archive": "<tarball path>",
#      "extracted_to": "<dir>",
#      "journals": ["..."],
#      "namespace_pod_logs": "<dir or empty string>",
#      "highlights": [{"file": "...", "line": N, "text": "..."}]
#   }]}
#
# Extraction is idempotent: directories with an existing index.json are
# skipped.
#
# Progress/errors: stderr. Absence of sosreports is NOT an error — the
# caller records it as an analysis gap.

HIGHLIGHT_RE='panic|OOM|oom-kill|segfault|Failed to start|level=error|FATAL|leader election lost'
MAX_HIGHLIGHTS=100

usage() {
    echo "Usage: $(basename "$0") <top-dir>" >&2
    exit 1
}

# Extract all sosreport-*.tar.xz in a single directory and write its
# sos-extracted/index.json.
extract_dir() {
    local artifacts_dir="${1}"
    local dest="${artifacts_dir}/sos-extracted"

    local -a tarballs=()
    while IFS= read -r t; do
        tarballs+=("${t}")
    done < <(find "${artifacts_dir}" -maxdepth 1 -name 'sosreport-*.tar.xz' | sort)

    if [[ -f "${dest}/index.json" ]]; then
        echo "Cached: ${dest}/index.json" >&2
        return 0
    fi

    if [[ ${#tarballs[@]} -eq 0 ]]; then
        return 0
    fi

    echo "Found ${#tarballs[@]} sosreport(s) in ${artifacts_dir}" >&2

    local result='{"sosreports": []}'
    local tarball
    for tarball in "${tarballs[@]}"; do
        local name
        name="$(basename "${tarball}" .tar.xz)"
        local outdir="${dest}/${name}"

        echo "  extracting: ${name}" >&2
        mkdir -p "${outdir}"
        # Sosreport tarballs contain a single top-level directory named
        # after the archive — strip it so files land directly in outdir.
        tar --no-same-owner --strip-components=1 -xf "${tarball}" -C "${outdir}"

        # Index high-signal locations. Journal command output lands under
        # per-plugin dirs (sos_commands/logs/, sos_commands/microshift/, ...).
        local journals_json
        journals_json=$(find "${outdir}" \
            \( -path '*/sos_commands/*journalctl*' -o -path '*/var/log/journal/*' \) \
            -type f 2>/dev/null | sort | jq -R . | jq -s .)

        local ns_logs
        ns_logs=$(find "${outdir}" -type d -path '*/sos_commands/*/namespaces' 2>/dev/null | head -1)

        # Pre-grep highlights across journals, component command output, and
        # dead-container logs (previous.log explains why a container exited).
        local -a scan_targets=()
        while IFS= read -r f; do
            scan_targets+=("${f}")
        done < <(find "${outdir}" \
            \( -path '*/sos_commands/*journalctl*' -o -path '*/sos_commands/*/inspect_*' \
               -o -path '*/namespaces/*/logs/previous.log' \) \
            -type f 2>/dev/null | sort)

        local highlights_json="[]"
        if [[ ${#scan_targets[@]} -gt 0 ]]; then
            # Grep high-signal patterns and parse each match into a
            # {file, line, text} JSON object for the index.
            highlights_json=$({ grep -nHIE "${HIGHLIGHT_RE}" "${scan_targets[@]}" 2>/dev/null || true; } \
                | head -${MAX_HIGHLIGHTS} \
                | jq -R 'capture("^(?<file>[^:]+):(?<line>[0-9]+):(?<text>.*)$")
                         | {file: .file, line: (.line | tonumber), text: (.text[0:200])}' \
                | jq -s .)
        fi

        result=$(echo "${result}" | jq \
            --arg archive "${tarball}" \
            --arg outdir "${outdir}" \
            --argjson journals "${journals_json}" \
            --arg nslogs "${ns_logs}" \
            --argjson highlights "${highlights_json}" \
            '.sosreports += [{
                archive: $archive,
                extracted_to: $outdir,
                journals: $journals,
                namespace_pod_logs: $nslogs,
                highlights: $highlights
            }]')
    done

    mkdir -p "${dest}"
    echo "${result}" > "${dest}/index.json"
    echo "Index written to ${dest}/index.json" >&2
}

main() {
    [[ ${#} -ne 1 ]] && usage
    local top_dir="${1}"

    [[ -d "${top_dir}" ]] || { echo "Error: not a directory: ${top_dir}" >&2; exit 1; }

    local sos_dirs
    sos_dirs=$(find "${top_dir}" -name 'sosreport-*.tar.xz' -printf '%h\n' 2>/dev/null | sort -u)

    if [[ -z "${sos_dirs}" ]]; then
        echo "No sosreports found under ${top_dir}" >&2
        return 0
    fi

    echo "=== Extracting sosreports ===" >&2
    local count=0
    while IFS= read -r d; do
        extract_dir "${d}" && ((count++)) || true
    done <<< "${sos_dirs}"
    echo "  Extracted sosreports in ${count} directory(ies)" >&2
}

main "${@}"
