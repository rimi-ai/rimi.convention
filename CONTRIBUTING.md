# Contributing to rimi.

*[Français plus bas](#contribuer-à-rimi)*

Thank you. The convention is only worth the consensus behind it.

## Before you start

- The reference text is [en.md](en.md). [fr.md](fr.md) is the official translation. **Every change to one must be made to the other in the same pull request.** If you can only write one language, say so in the PR: a maintainer or another contributor will add the other.
- Rule identifiers (`CONV-NNN`, `CONC-NNN`, `SOB-NNN`, `P-NN`) are never reused, even after a rule is Retired.
- Keywords follow RFC 2119: MUST, MUST NOT, SHOULD, MAY (French: DOIT, NE DOIT PAS, DEVRAIT, PEUT).

## Ways to contribute

| You want to… | Use |
| --- | --- |
| Propose a new rule | Issue form *Propose a rule* |
| Report a real case where an LLM guessed, invented or looped | Issue form *Real case* |
| Object to a rule | Issue form *Objection* |
| Ask a question, explore an idea | Discussions |
| Fix wording, a typo, a translation | Pull request |
| Move a rule to a new status | Pull request that links the evidence |

## What makes a good rule

A rule follows the template in [en.md](en.md#rule-template). It must be:

1. **Verifiable**: someone else can tell whether a response is conformant.
2. **Model-agnostic**: no dependency on a vendor, a model or an industry.
3. **Announced**: when the LLM applies the convention, it says so in one sentence.
4. **Correctable**: the user can override it in the next turn.
5. **Evidenced**: at least one real, anonymised example and one test case (a conformant and a non-conformant response).

## Real cases: privacy first

Remove names, phone numbers, emails, booking references, prices tied to a person, internal system names and anything that identifies a company or a customer. Paraphrase if needed. Do not paste production logs.

## Status changes

| Transition | Evidence required in the PR |
| --- | --- |
| Draft → Proposed | Complete template, one real case, one test case |
| Proposed → Accepted | Link to a public discussion open for at least 14 days, every objection answered |
| Accepted → Stable | Test results on at least 3 models from different providers |
| → Retired | Reason and, if any, the replacing rule |

## Style

Short sentences. One obligation per bullet. No marketing words. Sources go in the *Origin and sources* section, not inline.

## Licence of contributions

By contributing, you agree to dedicate your contribution to the public domain under [CC0 1.0](LICENSE).

---

## Contribuer à rimi.

- Le texte de référence est [en.md](en.md), la traduction officielle est [fr.md](fr.md). **Toute modification se fait dans les deux langues, dans la même pull request.** Si vous n'écrivez qu'une langue, signalez-le : quelqu'un complétera.
- Proposer une règle, signaler un cas réel, objecter : utilisez les formulaires d'issue. Questions et idées : Discussions.
- Une bonne règle est vérifiable, indépendante des modèles, annoncée par le LLM, corrigeable par l'utilisateur, et appuyée par un cas réel anonymisé et un cas de test.
- Anonymisez tout cas réel : aucun nom, numéro, email, référence de dossier ni nom de système interne.
- Les identifiants ne sont jamais réattribués.
- En contribuant, vous placez votre contribution dans le domaine public (CC0 1.0).
