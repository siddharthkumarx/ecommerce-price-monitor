#!/bin/sh
# Commit-message policy check: fails if any commit in the range (default: all of
# HEAD) has a trailer other than Signed-off-by, or a "Generated with" footer
# (.githooks/forbidden-footer). .githooks/commit-msg applies the same policy locally.
set -eu

range="${1:-HEAD}"
footer="$(git rev-parse --show-toplevel)/.githooks/forbidden-footer"
status=0

for sha in $(git rev-list "$range"); do
  msg="$(git log -1 --format=%B "$sha")"
  # Drop "---" lines first: git stops reading trailers at "---", which would hide them.
  extra="$(printf '%s\n' "$msg" | grep -vE '^[[:space:]]*-{3,}[[:space:]]*$' \
    | git interpret-trailers --parse | grep -viE '^signed-off-by:' || true)"
  if [ -n "$extra" ]; then
    echo "::error::commit $sha has a trailer other than Signed-off-by: $(printf '%s' "$extra" | cut -d: -f1 | paste -sd, -)"
    status=1
  fi
  if printf '%s\n' "$msg" | grep -qiEf "$footer"; then
    echo "::error::commit $sha has a \"Generated with\" footer"
    status=1
  fi
done

[ "$status" -eq 0 ] && echo "commit messages follow the policy ($(git rev-list --count "$range") checked)"
exit "$status"
