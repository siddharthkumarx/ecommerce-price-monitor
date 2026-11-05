# Publish record and remaining steps

## Done (2026-11-05)

The repository was published in place: switched from private to public, renamed
`siddharthkumarx/ecommerce-price-monitor`, default branch renamed `main`. The
history of `main` was then rewritten once with `git filter-repo` and force-pushed:
`docs/private/` removed from every commit, commit signatures dropped, the working
notes renamed to `docs/maintainers.md`; authors, dates and the data commits kept.

Also done on 2026-11-05: pull request #1 closed and its branch removed; alert
issue #2 closed (INC-006); `BFCM_RUNS_PER_DAY` set to "4"; the Pages deploy job
added to `daily.yml` (D-026).

## Still to do (owner, in the GitHub UI or a local clone)

1. **Settings, General:** paste the About text, website and topics from
   `docs/repo-settings.md`; upload `assets/social-preview.png` as the social preview.
2. **Pages:** Settings, Pages, Build and deployment, Source: "GitHub Actions".
   Settings, Secrets and variables, Actions, Variables: add `PAGES_ENABLED` = `true`.
   The next `daily` run deploys the dashboard; then run a Lighthouse audit and record
   it in `docs/decisions.md`.
3. **Release tag `data-2026-11`:** move it to the rewritten commit (the session's git
   proxy refused tag pushes). From a local clone:
   `git fetch origin && git tag -f data-2026-11 1e21f037782b8e24f01947ed2a0e06cafeaf154d && git push --force origin refs/tags/data-2026-11`
4. **Google Sheet (optional):** add the secret `GOOGLE_SA_JSON` and the variable
   `GOOGLE_SHEET_ID`, share the sheet with the service account, publish it
   view-only, and put its link in `config/public.yml` (`sheet:`).
