# Changelog

All notable changes to the convention are listed here. Versions follow [GOVERNANCE.md](GOVERNANCE.md#versions).

## [Unreleased]

## [0.3.1] — 2026-09-22

Patch. **No obligation changed**: the diff against 0.3.0 touches the observed-drift column and nothing else, and that was checked cell by cell before the version was raised.

### Changed

- Four real cases added, each verified against a primary trace rather than against a lesson written after the fact: CONV-015, CONV-016, CONV-027, CONV-030. Four other candidates were dropped for want of such a trace, one of them because its own source retracted the claim.
- Two predictions that sat in the observed-drift column are now marked as predictions (CONV-007, CONV-011). A column of observed drifts should not carry what has not been observed.
- The frozen-copy check verifies content, not only the fingerprint: it rebuilds each published version from the text of its own tag and compares field by field. A fingerprint answers for the text, and the text does not move — an obligation edited inside a published copy left it untouched. Found in a follow-up external review, with the translation check, which now also reads the body of every rule written out in full and not only its table rows.

### Added

- `convention.json`, the machine-readable projection of en.md: every rule with its type, status, wave, principle, obligations and the fingerprint of its text, plus the levels and the test-protocol thresholds. Rebuilt and checked on every change, signed at each release without any private key (Sigstore keyless, provenance attestation), published at <https://rimi-ai.github.io/rimi.convention/convention.json> and frozen per version under `versions/`.
- A release also signals `rimi.tests`: a `repository_dispatch` carrying the version, the fingerprint and the release URL. It announces, it never changes a rule and nothing merges automatically.

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
