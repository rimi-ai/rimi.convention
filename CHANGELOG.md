# Changelog

All notable changes to the convention are listed here. Versions follow [GOVERNANCE.md](GOVERNANCE.md#versions).

## [0.3.0] — 2026-09-17

Changes made after three external reviews (ChatGPT, Gemini, Claude).

### Added

- Rule types: invariant, default convention, informative; CONV-001 marked as a default convention.
- Review in five weekly waves; wave 1 is a core of 15 rules.
- Test protocol: machine-readable cases, variants, runs, judge, thresholds, report.
- Mapping table to OpenAI Model Spec, Microsoft HAX, NIST AI 600-1, OWASP, AI Act, ISO/IEC 42001.
- Conformance semantics: no level claim while rules are Draft or Proposed, who declares, what a level is not, use of the name.

### Changed

- SOB-009: tokens are measured and published; energy is a derived estimate with a cited factor, never presented as a measurement.
- Stable status: test protocol passed on at least 3 providers and 5 models, over two campaigns.
- Level A: invariants, plus either the rimi. default convention or a declared alternative.

## [0.2.0] — 2026-09-17

### Added

- SOB-019, periodic tasks: a recurring check must not wake an LLM when a simple automatic check can do it.
- SOB-020, routing by difficulty: each request goes to the smallest capable model, with mandatory escalation and no loss of declared reliability.
- Sources: FrugalGPT (2023), RouteLLM (2024).

## [0.1.0] — 2026-09-17

First public draft.

### Added

- Reference text in English ([en.md](en.md)) and official French translation ([fr.md](fr.md)).
- Principles P-01 to P-14 (P-11 to P-14 candidates).
- Part A: CONV-001 to CONV-035 (CONV-001 Proposed, others Draft).
- Part B: CONC-001 to CONC-011 (Draft).
- Part C: SOB-001 to SOB-018, frugality rules (Draft).
- Conformance levels A, AA, AAA and frugality indicator S1, S2, S3.
- Consensus process, contribution guide, governance, code of conduct, issue forms.
- Licence CC0 1.0.
