# Prior art, and what we owe it

This convention did not appear from nothing, and several of its rules exist because someone else did the work first. This file names them. It grows as the convention does.

## Review that changed the text

The statistical analysis of our test protocol came from an external reviewer who executed this repository rather than reading it, and demonstrated by sabotage that our pass rule could not decide: at 50 runs and a 95% bar, two teams testing the same conformant system reach opposite verdicts roughly half the time, and a perfect system fails once in five when judged by a judge with a 3% false-fail rate.

That review is why v0.4.0 will carry three-outcome verdicts with exact intervals instead of a binary pass. It also produced the real case now filed as issue #8, and pointed out that a released version could be silently rewritten — a defect we reproduced and closed.

The reviewer offered code under CC0. We did not use it: the tools in `tools/` were written here, in the style of the existing ones. The finding is theirs; the implementation is ours.

*Attribution to be completed by the reviewer, who is welcome to claim, correct or expand this paragraph.*

## Work we build on

**Standardising agent evaluation.** Ali El Filali and Inès Bedar, *Towards More Standardized AI Evaluation: From Models to Agents* (arXiv:2602.18029, 2026), argue that evaluation needs shared protocols and methodologies rather than more benchmarks, and that conventions are needed around inference configuration, environment setup and trace documentation. This convention is one attempt at the object they describe. Where they set out what such a discipline requires, we are trying to write one instance of it and see what breaks.

**Abstention.** CONV-002 — say that a value is missing rather than producing it — is the conversational form of a question studied under the name abstention. *Know Your Limits: A Survey of Abstention in Large Language Models* (arXiv:2407.18418) maps the field; *AbstentionBench* measures it on unanswerable questions. Our contribution is narrower and differently shaped: not whether a model knows the answer, but whether it distinguishes a value present in a tool result from one it computed itself.

**Execution harnesses.** promptfoo and DeepEval run tests against models; Giskard tests and red-teams agents. They are harnesses: they provide the pipe, and leave the practitioner to write the norm. This convention is the norm, not the pipe, and the two are complementary rather than competing — a distinction we got wrong in an early review and correct here. Our own runner, [rimi.tests](https://github.com/rimi-ai/rimi.tests), duplicates part of what promptfoo already does. We would rather contribute cases to an existing harness than maintain a second one.

## Frameworks the rules are mapped against

The mapping table in [en.md](en.md#mapping-to-existing-frameworks) states, rule by rule, what is new and what merely restates an obligation that already exists in the OpenAI Model Spec, Microsoft HAX guidelines, NIST AI 600-1, OWASP's LLM risks, the EU AI Act and ISO/IEC 42001. Where a rule restates, the source is the authority and this convention is only a more testable phrasing of it.

## How to be added here

If this convention states something you published first, open an issue. We will cite you, or explain why we think the rules differ. Being wrong about prior art is a defect like any other, and it is fixed the same way.
