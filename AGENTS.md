# Witcher Quest Atlas

- Keep the generated site inside `dist/`; frozen inputs under `evidence/` are read-only.
- Publish through `.github/workflows/pages.yml`; bind every release to its exact Git source commit in `version.json`.
- Rebuild exploration layers with `python3 scripts/build-exploration.py`. After exploration changes run `python3 scripts/validate-exploration.py` and `node scripts/validate-exploration.cjs`; retain the duplicate/deferred ledger and stable source-key IDs.
- Source inputs are frozen in `evidence/upstream/`. Never claim full in-game verification from data checks or browser tests.
- Use `python3 scripts/build-data.py` followed by `python3 scripts/enrich-data.py` and `python3 scripts/expand-catalog.py`, then `python3 scripts/build-guidance.py` to rebuild the catalog. These use frozen source facts and independently authored Chinese summaries.
- After meaningful changes, run `node scripts/validate.cjs` and the applicable browser checks. Save evidence and update `dist/validation.json` and `dist/validation-report.md`.
- Distinguish community discovery coordinates, approximate landmark anchors, automatic story triggers, and unknown coordinates. Do not invent quest-giver locations.
- A quest with no curated decisions must remain visibly marked as not fully reviewed; never describe it as having no consequences.
- Default to hidden spoilers. Reveal only the selected quest unless the user chooses the global spoiler control.
- Preserve the existing public audience; never change access to enable publishing.

- Use https://github.com/StormTian/witcher-quest-atlas as the source repository and `origin`. Preserve the existing Git commits and tags.
- Development may run locally or in CI. Use configurable Node/Python/Playwright/Chromium paths. Preserve historical evidence and label every new result with its actual environment and timestamp. Tool unavailability must be reported, never substituted with fake browser/game validation.
- Do not create periodic automation unless requested.

- Personal records are explicitly device-local. Preserve the versioned backup schema, stable object/decision IDs, unmatched-record ledger, validated import preview and default spoiler protection. Run `node scripts/validate-progress.cjs` after persistence or routing changes.

- Expanded catalogue uses the reviewed source-ID ledger in `evidence/catalog-review/reconciliation.json`. Keep all 267 legacy IDs and classifications; merge objectives/components/stages explicitly. Run both `scripts/validate-catalog.py` and `scripts/validate-catalog.cjs` after catalogue/type changes.

- Personal completion is not game success. Story facts default to unknown; preserve source all/any/active states and stage-failure exceptions. Run `node scripts/validate-guidance.cjs` and `node scripts/browser-guidance.cjs`; incoming effects obey target-task spoiler reveal and dependent node validity. All browser evidence must match `scripts/runtime-inputs.json`.
