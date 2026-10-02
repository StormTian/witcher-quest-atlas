# Witcher Quest Atlas

- Keep the generated site inside `dist/`; parent `sources/` is read-only.
- Preserve `.openai/hosting.json` and the existing Site identity.
- Source inputs are frozen in `evidence/upstream/`. Never claim full in-game verification from data checks or browser tests.
- Use `python3 scripts/build-data.py` followed by `python3 scripts/enrich-data.py` to rebuild the catalog. These use frozen source facts and independently authored Chinese summaries.
- After meaningful changes, run `node scripts/validate.cjs` and the applicable browser checks. Save evidence and update `dist/validation.json` and `dist/validation-report.md`.
- Distinguish community discovery coordinates, approximate landmark anchors, automatic story triggers, and unknown coordinates. Do not invent quest-giver locations.
- A quest with no curated decisions must remain visibly marked as not fully reviewed; never describe it as having no consequences.
- Default to hidden spoilers. Reveal only the selected quest unless the user chooses the global spoiler control.
- Keep new publications private unless the user explicitly changes access.
