# Publish checklist (private work repo to public portfolio repo)

Do these in order. Nothing here runs automatically.

1. **Never rename or make public this repository.** It keeps its full working
   history and stays private. Publish into a **fresh public repository**,
   `siddharthkumarx/ecommerce-price-monitor`, whose `main` branch starts clean: one
   initial commit made from a prepared copy of this tree (for example a fresh
   `git init` in an export of the files), with the identity and commit-message
   policy in the maintainers' guide. The badges and links assume `config/public.yml`
   (repo and branch `main`).
2. **Prepare the copy before that first commit:**
   - drop `docs/private/` (the call explainer);
   - rename the maintainers' guide to `docs/maintainers.md` and update the files that point to
     it (`docs/build-progress.md`, this checklist; `grep -rni "claude"` must find
     nothing);
   - optionally drop `checks/results/*/data/` (dry-run snapshots: the same public
     prices as `data/`);
   - run `uv run pytest` (the link check catches a missed reference) and
     `scripts/check-commit-messages.sh` in the new repository.
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
