# Governance

*[Français plus bas](#gouvernance)*

## Principles

- **Rough consensus, not votes** (RFC 7282). A rule is Accepted when no serious objection remains unanswered, not when a majority agrees. Polls in Discussions inform the editor; they do not decide.
- **Everything in the open.** Proposals, objections and decisions happen in public issues, Discussions and pull requests.
- **Evidence over opinion.** A real case and a test case weigh more than an argument without either.

## Roles

| Role | Who | Responsibilities |
| --- | --- | --- |
| Contributor | Anyone | Proposes rules, reports cases, objects, reviews |
| Editor (v0) | Hiram | Records consensus, merges, resolves deadlocks, publishes versions |
| Editorial board (from v1) | At least 3 people from different organisations | Replaces the single editor; decisions need no standing objection within the board |

The editor must explain every decision that closes a discussion, in writing, with a link to the evidence.

## Versions

Semantic versioning applied to the text:

- **Patch** (0.1.x): wording, typos, translation, no change to obligations.
- **Minor** (0.x.0): new rules, status changes, new test cases.
- **Major** (x.0.0): a change that can make a previously conformant system non-conformant.

A conformance claim always names the version: `rimi. AA · S2 (v0.1.0)`.

## Labels

`status:draft` `status:proposed` `status:accepted` `status:stable` `status:retired` · `part:A` `part:B` `part:C` `principle` · `type:new-rule` `type:real-case` `type:objection` `type:editorial` · `lang:en` `lang:fr` `needs-translation` · `discussion-open`

## Moving to v1

The single-editor phase ends when at least 3 people from different organisations have each contributed an Accepted rule or a Stable test result, and agree to sit on the board.

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## Gouvernance

- Consensus approximatif, pas de vote : une règle est acceptée quand aucune objection sérieuse ne reste sans réponse.
- Tout se passe en public, et la preuve (cas réel, cas de test) pèse plus que l'opinion.
- En v0, l'éditeur (Hiram) constate le consensus, fusionne, tranche les blocages et justifie chaque décision par écrit. À partir de v1, un comité d'au moins 3 personnes d'organisations différentes le remplace.
- Versions sémantiques : correctif (formulation), mineure (nouvelles règles, statuts), majeure (changement qui peut rendre non conforme un système qui l'était).
- Toute déclaration de conformité cite la version : `rimi. AA · S2 (v0.1.0)`.
