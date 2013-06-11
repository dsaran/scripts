#!/bin/bash
# Script to find recursively last modified log files

printUsage() {
    echo "usage: $0 [now|today|lasthour]"
}

WHEN=${1:-now}

case $WHEN in
    now)
        DATE_PATTERN="%j-%H:%M"
        ;;
    today)
        DATE_PATTERN="%j"
        ;;
    lasthour)
        DATE_PATTERN="%j-%H"
        ;;
    *) 
        printUsage
        exit 1
        ;;
esac

LS_CMD="ls --time-style=+$DATE_PATTERN -l"
set -x

for f in `find . -iname \*.log -mtime 0 2>/dev/null`; do $LS_CMD "$f"| awk '{print $6" "$7}'; done |grep `date +$DATE_PATTERN` |cut -d" " -f 2

