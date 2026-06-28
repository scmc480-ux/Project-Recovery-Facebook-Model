# Repository Structure

This repository is the public engine surface for Project Recovery.

It intentionally excludes the private operational workspace:

- no active jobs
- no client evidence
- no checkpoints
- no private manifests
- no generated release bundles
- no local AI runtime folders

## Public Engine Layout

```text
recovery_engine/
  intake/              source containers and inventory
  readers/facebook/    Facebook Reader v1
  normalize/           source-to-object normalization
  objects/             object schema constants
  reports/             canonical tree, reports, workbooks
  validation/          object validation and privacy checks
  utils/               hashing, JSONL, XLSX helpers

docs/                  public architecture and release notes
examples/              fictional sample data only
scripts/               public helper scripts
tests/                 clean-clone verification
```

## Private Workspace Mapping

The private development workspace may contain folders such as `jobs/`,
`intake/`, `workspace/`, `CHECKPOINTS/`, and `outputs/`. Those are runtime
surfaces and should not be copied into this public repository.

Reusable behavior from the private workspace should be promoted into
`recovery_engine/` only after it is:

- generalized
- stripped of private paths
- covered by fictional examples
- validated by tests
- documented as public API or internal engine behavior
