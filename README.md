<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <img src="assets/logo-light.svg" alt="rimi. — Open Convention for Conversational Reliability of LLMs" width="320">
  </picture>
</h1>

<p align="center"><strong>Open Convention for Conversational Reliability of LLMs</strong></p>

<p align="center"><strong>For responsible AI: reliable, frugal, honest.</strong> · green friendly</p>

<p align="center"><em>rimi. is read "rimi dot".</em> · <a href="#français">Français</a></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg" alt="License: CC0-1.0"></a>
  <img src="https://img.shields.io/badge/version-0.2.0-blue" alt="Version 0.2.0">
  <img src="https://img.shields.io/badge/status-draft-orange" alt="Status: draft">
  <a href="https://doi.org/10.5281/zenodo.22814989"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.22814989.svg" alt="DOI 10.5281/zenodo.22814989"></a>
  <picture><source media="(prefers-color-scheme: dark)" srcset="assets/green-friendly-dark.svg"><img src="assets/green-friendly-light.svg" alt="green friendly" height="28"></picture>
</p>

---

**Contents:** [What this is](#what-this-is) · [The "yes" example](#the-yes-example) · [What is inside v0.2.0](#what-is-inside-v020) · [Conformance levels](#conformance-levels) · [Rule lifecycle](#rule-lifecycle) · [Honest scope](#honest-scope) · [How to take part](#how-to-take-part) · [Licence](#licence) · [How to cite](#how-to-cite) · [Origin](#origin) · [Français](#français)

## What this is

A user asks an assistant: *"Option 1 or option 2?"* The user answers: *"Yes."*

Today, every LLM does something different: it guesses, it asks again, it loops, sometimes it invents. **rimi.** proposes a convention known in advance: *"yes" counts as option 1, the LLM says so, and the user corrects if needed.* No loop, no silent guess.

This repository holds a growing set of such conventions: short, testable rules that say what an LLM does when it would otherwise guess, smooth over or invent. They are independent of any model, provider or industry.

- **The convention (reference text, English):** [en.md](en.md)
- **Official French translation:** [fr.md](fr.md)

## The "yes" example

| Without a convention | With rimi. (CONV-001) |
| --- | --- |
| **Assistant:** Option 1, direct flight at 2 pm, or option 2, 9-hour stopover?<br>**User:** Yes.<br>**Assistant:** *guesses one of the two, or asks the same question again, and again.* | **Assistant:** Option 1, direct flight at 2 pm, or option 2, 9-hour stopover?<br>**User:** Yes.<br>**Assistant:** I'm going with option 1. Say 2 if you preferred the other one. |

## What is inside v0.2.0

| Part | Content | Status |
| --- | --- | --- |
| Principles | P-01 to P-14 | P-11 to P-14 candidates |
| Part A | CONV-001 to CONV-035: model behaviour in conversation | CONV-001 Proposed, others Draft |
| Part B | CONC-001 to CONC-011: design rules for prompts and tools | Draft |
| Part C | SOB-001 to SOB-020: frugality for designers, models and requesters | Draft |

## Conformance levels

Conformance levels, inspired by WCAG: **A · AA · AAA** for reliability, plus a separate frugality indicator **S1 · S2 · S3**. Example claim: `rimi. AA · S2 (v0.2.0)`.

| Reliability | Requirement |
| --- | --- |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/level-A-dark.svg"><img src="assets/level-A-light.svg" alt="rimi. level A" height="24"></picture> | All MUST and MUST NOT obligations of Part A, with status Accepted or Stable |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/level-AA-dark.svg"><img src="assets/level-AA-light.svg" alt="rimi. level AA" height="24"></picture> | Level A, plus all MUST and MUST NOT obligations of Part B |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/level-AAA-dark.svg"><img src="assets/level-AAA-light.svg" alt="rimi. level AAA" height="24"></picture> | Level AA, plus all SHOULD recommendations of both parts |

| Frugality | Requirement |
| --- | --- |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/sob-S1-dark.svg"><img src="assets/sob-S1-light.svg" alt="rimi. frugality S1" height="24"></picture> | All MUST and MUST NOT obligations of Part C |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/sob-S2-dark.svg"><img src="assets/sob-S2-light.svg" alt="rimi. frugality S2" height="24"></picture> | S1, plus the published measurement (SOB-009) |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/sob-S3-dark.svg"><img src="assets/sob-S3-light.svg" alt="rimi. frugality S3" height="24"></picture> | S2, plus all SHOULD recommendations of Part C addressed to the designer and the LLM |

Reliability comes first: a frugal answer that is wrong is not a saving.

## Rule lifecycle

```mermaid
flowchart LR
  A[Draft] --> B[Proposed]
  B --> C[Accepted]
  C --> D[Stable]
  B --> E[Retired]
  C --> E
```

A rule is Accepted after at least 14 days of public discussion with no objection left unanswered (rough consensus, RFC 7282). It is Stable once its test cases pass on at least 3 models from different providers.

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

## Licence

[CC0 1.0](LICENSE): public domain. Use it, copy it, build on it, in open or commercial products, with no permission needed. A citation is appreciated but not required.

Logo and badges composed with [Geist](https://github.com/vercel/geist-font) (SIL Open Font License 1.1).

## How to cite

See [CITATION.cff](CITATION.cff).

> Hiram (2026). *rimi. — Open Convention for Conversational Reliability of LLMs*, version 0.2.0. Zenodo. https://doi.org/10.5281/zenodo.22814989

This DOI always resolves to the latest version. Each version also has its own DOI on Zenodo (v0.2.0: [10.5281/zenodo.22816833](https://doi.org/10.5281/zenodo.22816833)).

## Origin

The method comes from audits of production prompts, read as normative texts. Its principles draw on a tradition of textual interpretation; details and sources are at the end of [en.md](en.md#origin-and-sources).

---

## Français

**rimi. — pour une IA responsable : fiable, sobre, loyale.** · green friendly

**Sommaire :** [En bref](#fr-en-bref) · [L'exemple du « oui »](#fr-oui) · [Contenu de la v0.2.0](#fr-contenu) · [Niveaux de conformité](#fr-niveaux) · [Cycle de vie des règles](#fr-cycle) · [Participer](#fr-participer) · [Licence](#fr-licence) · [Citer](#fr-citer) · [Origine](#fr-origine)

<a id="fr-en-bref"></a>
### En bref

Un utilisateur répond « oui » à la question « option 1 ou option 2 ? ». Plutôt que de deviner ou de tourner en boucle, le LLM applique une convention connue d'avance : « oui » vaut option 1, il l'annonce, et l'utilisateur corrige si besoin.

**rimi.** rassemble ces conventions : des règles courtes, testables, indépendantes de tout modèle, fournisseur ou secteur.

- Texte de référence (anglais) : [en.md](en.md)
- Traduction officielle française : [fr.md](fr.md)

<a id="fr-oui"></a>
### L'exemple du « oui »

| Sans convention | Avec rimi. (CONV-001) |
| --- | --- |
| **Assistant :** Option 1, vol direct à 14h, ou option 2, escale de 9h ?<br>**Utilisateur :** Oui.<br>**Assistant :** *devine l'une des deux, ou repose la même question, encore et encore.* | **Assistant :** Option 1, vol direct à 14h, ou option 2, escale de 9h ?<br>**Utilisateur :** Oui.<br>**Assistant :** Je retiens l'option 1. Dites 2 si vous préfériez l'autre. |

<a id="fr-contenu"></a>
### Contenu de la v0.2.0

| Partie | Contenu | Statut |
| --- | --- | --- |
| Principes | P-01 à P-14 | P-11 à P-14 candidats |
| Partie A | CONV-001 à CONV-035 : comportement du modèle dans la conversation | CONV-001 Proposée, les autres en Brouillon |
| Partie B | CONC-001 à CONC-011 : règles de conception des prompts et des outils | Brouillon |
| Partie C | SOB-001 à SOB-020 : sobriété pour les concepteurs, les modèles et les demandeurs | Brouillon |

<a id="fr-niveaux"></a>
### Niveaux de conformité

Niveaux de conformité inspirés des WCAG : **A · AA · AAA** pour la fiabilité, et un indicateur de sobriété distinct **S1 · S2 · S3**. Exemple de déclaration : `rimi. AA · S2 (v0.2.0)`.

| Fiabilité | Exigence |
| --- | --- |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/level-A-dark.svg"><img src="assets/level-A-light.svg" alt="rimi. niveau A" height="24"></picture> | Toutes les obligations DOIT et NE DOIT PAS de la partie A, statut Acceptée ou Stable |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/level-AA-dark.svg"><img src="assets/level-AA-light.svg" alt="rimi. niveau AA" height="24"></picture> | Niveau A, plus toutes les obligations DOIT et NE DOIT PAS de la partie B |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/level-AAA-dark.svg"><img src="assets/level-AAA-light.svg" alt="rimi. niveau AAA" height="24"></picture> | Niveau AA, plus toutes les recommandations DEVRAIT des deux parties |

| Sobriété | Exigence |
| --- | --- |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/sob-S1-dark.svg"><img src="assets/sob-S1-light.svg" alt="rimi. sobriété S1" height="24"></picture> | Toutes les obligations DOIT et NE DOIT PAS de la partie C |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/sob-S2-dark.svg"><img src="assets/sob-S2-light.svg" alt="rimi. sobriété S2" height="24"></picture> | S1, plus la mesure publiée (SOB-009) |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/sob-S3-dark.svg"><img src="assets/sob-S3-light.svg" alt="rimi. sobriété S3" height="24"></picture> | S2, plus toutes les recommandations DEVRAIT de la partie C destinées au concepteur et au LLM |

La fiabilité passe avant la sobriété : une réponse sobre mais fausse n'est pas une économie.

<a id="fr-cycle"></a>
### Cycle de vie des règles

```mermaid
flowchart LR
  A[Brouillon] --> B[Proposée]
  B --> C[Acceptée]
  C --> D[Stable]
  B --> E[Retirée]
  C --> E
```

Une règle est Acceptée après au moins 14 jours de discussion publique, sans objection restée sans réponse (consensus approximatif, RFC 7282). Elle devient Stable quand ses cas de test passent sur au moins 3 modèles de fournisseurs différents.

<a id="fr-participer"></a>
### Participer

- Issues : proposer une règle, signaler un cas réel, objecter.
- [Discussions](../../discussions) pour les questions et les idées.
- Pull requests en anglais et en français, dans la même PR. Voir [CONTRIBUTING.md](CONTRIBUTING.md).

<a id="fr-licence"></a>
### Licence

[CC0 1.0](LICENSE) : domaine public.

Logo et badges composés avec [Geist](https://github.com/vercel/geist-font) (SIL Open Font License 1.1).

<a id="fr-citer"></a>
### Citer

Voir [CITATION.cff](CITATION.cff).

> Hiram (2026). *rimi. — Open Convention for Conversational Reliability of LLMs*, version 0.2.0. Zenodo. https://doi.org/10.5281/zenodo.22814989

Ce DOI renvoie toujours à la dernière version. Chaque version a aussi son propre DOI sur Zenodo (v0.2.0 : [10.5281/zenodo.22816833](https://doi.org/10.5281/zenodo.22816833)).

<a id="fr-origine"></a>
### Origine

La méthode vient d'audits de prompts en production, lus comme des textes normatifs. Ses principes s'inspirent d'une tradition d'interprétation des textes ; détails et sources à la fin de [fr.md](fr.md#origine-et-sources).

Version 0.2.0, brouillon. La fiabilité passe avant la sobriété.
