# Project Recovery

<sub><em>Building tomorrow's recovery framework, one module at a time.</em></sub>

---

Project Recovery is a modular recovery engine for turning export archives into
source-defensible, normalized outputs.

This public repository contains **Facebook Reader v1** only. It is intentionally
not a copy of the private forensic workspace. Runtime jobs, evidence, working
folders, checkpoints, and release bundles stay outside this repository.

## What Facebook Reader v1 Does

- Reads Facebook JSON exports from folders or zip files.
- Reads lightweight Facebook HTML message exports.
- Normalizes messages, conversations, entities, events, and artifacts.
- Preserves source references, source hashes, truth class, and confidence.
- Validates normalized objects before output.
- Emits a canonical case output tree.
- Generates workbook files and Markdown reports.

## Public Repository Layout

```text
Project-Recovery/
  recovery_engine/
    intake/
    readers/facebook/
    normalize/
    objects/
    reports/
    validation/
    utils/
  docs/
  examples/
  scripts/
  tests/
```

## Quick Run

```powershell
python -m recovery_engine.cli facebook `
  --source examples/facebook_sample `
  --case-id SAMPLE_FACEBOOK_CASE `
  --output outputs
```

The finished case will appear at:

```text
outputs/SAMPLE_FACEBOOK_CASE/
```

## Canonical Output Model

Every processed case writes one human-facing output tree:

```text
outputs/<case_id>/
  00_README.md
  OUTPUT_INDEX.json
  OUTPUT_INDEX.md
  01_MASTER/
  02_DERIVED/
  03_WORKBOOKS/
  04_REPORTS/
  05_RELEASE/
  06_PROVENANCE/
  07_VALIDATION/
  08_LOGS/
  09_SYSTEM_REFERENCE/
```

The governing rule is:

```text
MASTER is recovered source truth.
DERIVED is interpretation or structure.
DERIVED must point back to MASTER.
```

## Governing Rules

Project Recovery follows this mission:

```text
Build the core for universality; build the modules for specificity.
```

Facebook Reader v1 is the first public reference specialization. See
`docs/GOVERNING_RULES.md` for the full governing rules.

## Privacy Boundary

The repository is designed to be safe for public development:

- No jobs are included.
- No private evidence is included.
- No real release bundles are included.
- Examples use synthetic identifiers only.
- Runtime output folders are ignored by Git.

Run the public-readiness check before publishing:

```powershell
python scripts/verify_public_repo.py .
```

If you ran the sample locally, remove the generated `outputs/` folder before
running the public-readiness check.

## Development

Run tests:

```powershell
python -m unittest discover -s tests
```

Run the sample:

```powershell
python scripts/run_facebook_reader.py `
  --source examples/facebook_sample `
  --case-id SAMPLE_FACEBOOK_CASE `
  --output outputs
```

See `CONTRIBUTING.md` and `SECURITY.md` before adding examples or public data.

---

# Project Ecosystem

### Project Recovery

<sub><em>Building tomorrow's recovery framework, one module at a time.</em></sub>

https://github.com/scmc480-ux/Project-Recovery

---

### Project Symphony

<sub><em>One Vision. Infinite Perspectives.</em></sub>

https://github.com/scmc480-ux/Project-Symphony

---

### Project Orchestra

<sub><em>Become the Conductor. Orchestrate Intelligence.</em></sub>

https://github.com/scmc480-ux/Project-Orchestra
