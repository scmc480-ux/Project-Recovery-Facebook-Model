# Public Release Checklist

Before publishing Project Recovery Facebook Reader v1:

- Run `python -m unittest discover -s tests`.
- Run `python scripts/verify_public_repo.py .`.
- Confirm no private `jobs/`, `intake/`, `workspace/`, `outputs/`, or `CHECKPOINTS/` folders are present.
- Delete any locally generated `outputs/` folder before release verification.
- Confirm examples are fictional.
- Confirm examples use synthetic identifiers only, such as `PERSON_001`, and do not contain real names, handles, emails, addresses, phone numbers, or real URLs.
- Confirm generated outputs are not committed.
- Confirm the README and QUICKSTART commands work from a clean clone.
- Confirm the package can run with only the Python standard library.
- Confirm `docs/GOVERNING_RULES.md` still matches the release scope.
