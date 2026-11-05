# Publish record and remaining steps

## Done (2026-11-05)

The repository was published in place: switched from private to public, renamed
`siddharthkumarx/ecommerce-price-monitor`, default branch renamed `main`. The
history of `main` was then rewritten once with `git filter-repo` and force-pushed:
`docs/private/` removed from every commit, commit signatures dropped, the working
notes renamed to `docs/maintainers.md`; authors, dates and the data commits kept.

## Still to do (owner, in the GitHub UI)

1. **Settings, General:** paste the About text, website and topics from
   `docs/repo-settings.md`; upload `assets/social-preview.png` as the social preview.
2. **Pull request #1 (Dependabot):** close it and delete its branch. It was opened
   on the old history, so it still carries the removed files. Dependabot opens a
   fresh one on the new history at its next monthly check.
3. **Release tag `data-2026-11`:** it points at a pre-rewrite commit (one without
   `docs/private/`). Moving it to the rewritten commit is a tag force-push; the
   monthly release workflow keeps working either way.
4. **Pages:** add the deploy step (`docs/build-progress.md` item 20), set Pages
   source to "GitHub Actions", and point `siddharthkumar.com/ecommerce-price-monitor/`
   at it. Then run a Lighthouse audit and record it in `docs/decisions.md`.
5. **Google Sheet (optional):** add the secret `GOOGLE_SA_JSON` and the variable
   `GOOGLE_SHEET_ID`, share the sheet with the service account, publish it
   view-only, and put its link in `config/public.yml` (`sheet:`).
6. **BFCM:** the repository is public before 26 Nov 2026, so the rule in D-021
   allows `env.BFCM_RUNS_PER_DAY: "4"` in `.github/workflows/daily.yml`.
