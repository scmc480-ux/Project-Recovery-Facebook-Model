# Contributing

Project Recovery welcomes public development on the reusable engine.

## Scope For This Repository

This repository currently accepts work for Facebook Reader v1 and shared engine
components needed by that reader.

Do not add:

- private case folders
- real Facebook exports
- generated outputs
- release bundles
- checkpoint folders
- personal names, handles, addresses, phone numbers, emails, or real URLs in examples
- new data-source readers outside the active release scope

## Before Opening A Pull Request

Run:

```bash
python -m unittest discover -s tests
python scripts/verify_public_repo.py .
```

When adding examples, use synthetic identifiers such as `PERSON_001`,
`THREAD_0001`, `POST_001`, and `PAGE_001`.

## Evidence Boundary

Real evidence belongs outside Git. The engine should read evidence as runtime
input and write outputs to ignored runtime folders.
