# rimi. — Open Convention for Conversational Reliability of LLMs

**For responsible AI: reliable, frugal, honest.** · green friendly

*rimi. is read "rimi dot".* · [Français](#français)

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](LICENSE) ![Version](https://img.shields.io/badge/version-0.1.0-blue) ![Status](https://img.shields.io/badge/status-draft-orange)

---

## What this is

A user asks an assistant: *"Option 1 or option 2?"* The user answers: *"Yes."*

Today, every LLM does something different: it guesses, it asks again, it loops, sometimes it invents. **rimi.** proposes a convention known in advance: *"yes" counts as option 1, the LLM says so, and the user corrects if needed.* No loop, no silent guess.

This repository holds a growing set of such conventions: short, testable rules that say what an LLM does when it would otherwise guess, smooth over or invent. They are independent of any model, provider or industry.

- **The convention (reference text, English):** [en.md](en.md)
- **Official French translation:** [fr.md](fr.md)

## What is inside v0.1.0

| Part | Content | Status |
| --- | --- | --- |
| Principles | P-01 to P-14 | P-11 to P-14 candidates |
| Part A | CONV-001 to CONV-035: model behaviour in conversation | CONV-001 Proposed, others Draft |
| Part B | CONC-001 to CONC-011: design rules for prompts and tools | Draft |
| Part C | SOB-001 to SOB-018: frugality for designers, models and requesters | Draft |

Conformance levels, inspired by WCAG: **A · AA · AAA** for reliability, plus a separate frugality indicator **S1 · S2 · S3**. Example claim: `rimi. AA · S2 (v0.1.0)`.

Reliability comes first: a frugal answer that is wrong is not a saving.

## Honest scope

This is a **v0 draft**. The rules come from real production audits of conversational agents (travel booking and other domains, anonymised). Most rules are still Draft: they need more real cases, test cases and public discussion before they become Accepted. Nothing here is a certification.

## How to take part

The consensus happens here, in the open, with GitHub's own tools.

- **Propose a rule** → open an issue with the *Propose a rule* form.
- **Report a real case** (an LLM that guessed, invented or looped) → *Real case* form.
- **Object to a rule** → *Objection* form. An objection must be answered before a rule is Accepted.
- **Discuss** → [Discussions](../../discussions).
- **Edit the text** → pull request. English and French must change together.

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [GOVERNANCE.md](GOVERNANCE.md) first.

Lifecycle: `Draft → Proposed → Accepted → Stable → Retired`. A rule is Accepted after at least 14 days of public discussion with no objection left unanswered (rough consensus, RFC 7282). It is Stable once its test cases pass on at least 3 models from different providers.

## Where it comes from

The method reads a system prompt the way a legal text is read: what it requires, what it forgets, where two rules clash, where a word is vague. That way of reading has a long history in the interpretive tradition of the Talmud (the schools of Rabbi Ishmael and Rabbi Akiva). A series of articles tells that story; the convention itself stays technical. Sources are listed at the end of [en.md](en.md).

## Licence

[CC0 1.0](LICENSE): public domain. Use it, copy it, build on it, in open or commercial products, with no permission needed. A citation is appreciated but not required.

## How to cite

See [CITATION.cff](CITATION.cff).

> Hiram (2026). *rimi. — Open Convention for Conversational Reliability of LLMs*, version 0.1.0. https://github.com/rimi-ai/rimi.convention

---

## Français

**rimi. — pour une IA responsable : fiable, sobre, loyale.** · green friendly

Un utilisateur répond « oui » à la question « option 1 ou option 2 ? ». Plutôt que de deviner ou de tourner en boucle, le LLM applique une convention connue d'avance : « oui » vaut option 1, il l'annonce, et l'utilisateur corrige si besoin.

**rimi.** rassemble ces conventions : des règles courtes, testables, indépendantes de tout modèle, fournisseur ou secteur.

- Texte de référence (anglais) : [en.md](en.md)
- Traduction officielle française : [fr.md](fr.md)
- Niveaux de conformité : A · AA · AAA, et indicateur de sobriété S1 · S2 · S3.
- Participer : issues (proposer une règle, signaler un cas réel, objecter), Discussions, pull requests en anglais et en français. Voir [CONTRIBUTING.md](CONTRIBUTING.md).
- Licence : CC0, domaine public.

Version 0.1.0, brouillon. La fiabilité passe avant la sobriété.
