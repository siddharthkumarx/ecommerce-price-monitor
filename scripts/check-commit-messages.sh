#!/bin/sh
# Fails if any commit in the given range (default: all of HEAD) carries a tool
# attribution line. Pattern is shared with .githooks/commit-msg.
set -eu

range="${1:-HEAD}"
pattern_file="$(git rev-parse --show-toplevel)/.githooks/attribution-pattern"
status=0

for sha in $(git rev-list "$range"); do
  if git log -1 --format=%B "$sha" | grep -qiEf "$pattern_file"; then
    echo "::error::commit $sha has an attribution line: $(git log -1 --format=%s "$sha")"
    status=1
  fi
done

[ "$status" -eq 0 ] && echo "commit messages OK ($(git rev-list --count "$range") checked)"
exit "$status"
