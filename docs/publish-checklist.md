# Publish checklist (private work repo to public portfolio repo)

Do these in order. Nothing here runs automatically.

1. **Remove private files.** Delete `docs/private/` (the call explainer) and
   `checks/results/*/data/latest/snapshot.csv` only if you do not want dry-run
   snapshots public (they hold the same public prices as `data/`). Commit.
2. **Create the public repository** `siddharthkumarx/ecommerce-price-monitor` with the
   default branch `main` (the README badges and links assume `config/public.yml`:
   repo and branch). Push this history to `main`.
3. **Settings, General:** paste the About text, website and topics from
   `docs/repo-settings.md`; upload `assets/social-preview.png` as the social preview.
4. **Settings, Actions, General:** allow Actions; workflow permissions "Read and
   write" (the daily run commits `data/` and the README, and uploads releases).
5. **Pages:** add the deploy step (`docs/build-progress.md` item 20), set Pages
   source to "GitHub Actions", and point `siddharthkumar.com/ecommerce-price-monitor/`
   at it. Then run a Lighthouse audit and record it in `docs/decisions.md`.
6. **Google Sheet (optional):** add the secret `GOOGLE_SA_JSON` and the variable
   `GOOGLE_SHEET_ID`, share the sheet with the service account, publish it
   view-only, and put its link in `config/public.yml` (`sheet:`).
7. **BFCM:** if public by 26 Nov 2026, set `env.BFCM_RUNS_PER_DAY: "4"` in
   `.github/workflows/daily.yml` (D-021).
8. **First public run:** start `daily` once from the Actions tab and check that the
   badges render (they read `data/badges/*.json` from the public `main` branch).
9. **Archive the private work repo** so its schedule stops (two repositories must not
   collect the same stores).
