#!/usr/bin/env bash
set -euo pipefail

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
BLUE=$'\033[0;34m'
NC=$'\033[0m'

usage() {
    cat <<EOF
Usage: $(basename "$0") [options]

Options:
  -n, --name <name>   Name to greet (default: World)
  -h, --help          Show this help message
EOF
}

NAME="World"

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            [[ $# -ge 2 ]] || { echo "${RED}Error:${NC} --name requires a value" >&2; exit 1; }
            NAME="$2"; shift 2
            ;;
        -h|--help) usage; exit 0 ;;
        -*) echo "${RED}Error:${NC} Unknown option: $1" >&2; exit 1 ;;
        *) NAME="$1"; shift ;;
    esac
done

echo "${GREEN}Hello, ${BLUE}${NAME}${GREEN}!${NC}"
