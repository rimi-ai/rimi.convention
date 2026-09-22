# Prior art, and what we owe it

This convention did not appear from nothing, and several of its rules exist because someone else did the work first. This file names them. It grows as the convention does.

## Review that changed the text

The statistical analysis of our test protocol came from an external reviewer who executed this repository rather than reading it, and demonstrated by sabotage that our pass rule could not decide: at 50 runs and a 95% bar, two teams testing the same conformant system reach opposite verdicts roughly half the time, and a perfect system fails once in five when judged by a judge with a 3% false-fail rate.

That review is why v0.4.0 will carry three-outcome verdicts with exact intervals instead of a binary pass. It also produced the real case now filed as issue #8, and pointed out that a released version could be silently rewritten.

That last defect took two passes to close, and we did not see the second one. The first pass stopped an ordinary build from overwriting a published copy. On 20 September 2026 the same reviewer came back and showed that the guard we had added answered for the text and not for the file: an obligation edited inside a frozen copy — MUST turned into SHOULD — left its fingerprint untouched, because the fingerprint covers the source. A second guard in the same review: the translation check compared table rows and never the body of a rule written out in full, so a DOIT could become a DEVRAIT in one language, in the rule most used as an example, and nothing said a word. Both are now checked by content, and both faults are planted in the test suite so that a check that stops seeing them fails. Claiming the first half closed was our error, not the reviewer's.

The reviewer offered code under CC0. We did not use it: the tools in `tools/` were written here, in the style of the existing ones. The finding is theirs; the implementation is ours.

*Attribution to be completed by the reviewer, who is welcome to claim, correct or expand this paragraph.*

## Work we build on

**Standardising agent evaluation.** Ali El Filali and Inès Bedar, *Towards More Standardized AI Evaluation: From Models to Agents* (arXiv:2602.18029, 2026), argue that evaluation needs shared protocols and methodologies rather than more benchmarks, and that conventions are needed around inference configuration, environment setup and trace documentation. This convention is one attempt at the object they describe. Where they set out what such a discipline requires, we are trying to write one instance of it and see what breaks.

**Abstention.** CONV-002 — say that a value is missing rather than producing it — is the conversational form of a question studied under the name abstention. *Know Your Limits: A Survey of Abstention in Large Language Models* (arXiv:2407.18418) maps the field; *AbstentionBench* measures it on unanswerable questions. Our contribution is narrower and differently shaped: not whether a model knows the answer, but whether it distinguishes a value present in a tool result from one it computed itself.

**Execution harnesses.** promptfoo and DeepEval run tests against models; Giskard tests and red-teams agents. They are harnesses: they provide the pipe, and leave the practitioner to write the norm. This convention is the norm, not the pipe, and the two are complementary rather than competing — a distinction we got wrong in an early review and correct here. Our own runner, [rimi.tests](https://github.com/rimi-ai/rimi.tests), duplicates part of what promptfoo already does. We would rather contribute cases to an existing harness than maintain a second one.

**Policies compiled into tests.** Microsoft's [ASSERT](https://github.com/responsibleai/ASSERT) turns a written policy into executable evaluations. The [Agent Control Specification](https://microsoft.github.io/agent-governance-toolkit/packages/agent-control-specification/) (ACS), from a separate Microsoft toolkit, defines the points in an agent's loop where behaviour can be checked and controlled. Neither prescribes what the behaviour should be: the policy is the practitioner's. The link from a written rule to an executable test is therefore not ours, and we do not claim it. What this convention supplies is the content such a tool compiles — rules already written, each with the real case and test cases it must carry to leave Draft — and a verdict rule that can say *inconclusive* instead of forcing a pass or a fail.

**Answers checked against tool outputs.** [attest](https://github.com/adepeju4/attest) measures whether an agent's answer fabricates content absent from its tool outputs, and reports the result with error bars. That is the closest existing work to CONV-002 we have found. The difference is in the instrument, not the question: its check uses a model to judge, ours is deterministic and needs no judge, which is what keeps a 0-in-60 result from depending on a judge's own error rate.

**Runtime guardrails.** [Invariant](https://github.com/invariantlabs-ai/invariant) enforces rules on an agent's traffic while it runs, in a policy language the operator writes, with a focus on security. It stops what is forbidden at the moment it happens; this convention states what a model should do and tests it before deployment. The two sit at different moments of the same life.

## Frameworks the rules are mapped against

The mapping table in [en.md](en.md#mapping-to-existing-frameworks) states, rule by rule, what is new and what merely restates an obligation that already exists in the OpenAI Model Spec, Microsoft HAX guidelines, NIST AI 600-1, OWASP's LLM risks, the EU AI Act and ISO/IEC 42001. Where a rule restates, the source is the authority and this convention is only a more testable phrasing of it.

## How to be added here

If this convention states something you published first, open an issue. We will cite you, or explain why we think the rules differ. Being wrong about prior art is a defect like any other, and it is fixed the same way.
