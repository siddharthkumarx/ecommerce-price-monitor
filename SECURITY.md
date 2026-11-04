# Security

Please report a vulnerability or a leaked secret privately to
hello@siddharthkumar.com, not in a public issue. You will get an answer within
48 hours.

This repository holds no credentials. The only secret it can use,
`GOOGLE_SA_JSON` (Google Sheet publishing), lives in GitHub Actions secrets and is
never printed. Every push is scanned with gitleaks, and dependencies are audited
with pip-audit in CI.
