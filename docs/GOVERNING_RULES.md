# Governing Rules

Project Recovery is built around a universal recovery-engine mission:

> Build the core for universality; build the modules for specificity.

Facebook Reader v1 is the first public reference specialization. It should
exercise the reusable core, not become a one-off endpoint that traps future work
inside Facebook-specific assumptions.

## Mission

Project Recovery exists to provide a modular recovery engine that can ingest
source exports, preserve provenance, normalize evidence into stable objects,
validate outputs, and publish canonical human-facing deliverables.

The public 1.0 release is scoped to Facebook Reader v1 only, but the engine
architecture should remain ready for future modules.

## Strategic Rule

Anything every future module will need belongs in the core.

Anything only some data types, platforms, workflows, or task classes need
belongs in a module.

## Core Responsibilities

The reusable core owns:

- intake and source inventory
- provenance capture
- normalized object contracts
- validation
- canonical output structure
- workbook and report generation
- privacy/release checks
- stable utility behavior such as hashing and JSONL/XLSX writing

## Module Responsibilities

Reader modules own:

- platform-specific parsing
- data-type-specific extraction logic
- source-format reconstruction behavior
- module-specific confidence notes
- module-specific mapping into the normalized object model

## Evidence Rules

- Verbatim recovered data is the truth layer.
- Derived objects must preserve source references.
- Missing data must stay visibly missing.
- Inference must not be presented as recovered fact.
- Personal evidence must never be committed to the public repository.
- Examples must use synthetic identifiers only.

## Public Release Scope

This repository currently publishes Facebook Reader v1. Do not add new data
source readers to this release line without explicitly updating the scope,
documentation, examples, tests, and release checklist.
