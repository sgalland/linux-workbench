# AI Capabilities Roadmap

Linux Workbench uses AI as a reasoning and orchestration layer around deterministic workstation management. The long-term goal is not an unrestricted AI shell. The goal is a workstation that can understand intent, explain state, investigate unfamiliar problems, propose safe plans, and turn solved problems into deterministic automation.

This roadmap is orthogonal to the numbered workstation batches in [roadmap.md](roadmap.md). Deferring a workstation-configuration batch does not automatically defer read-only AI work, and progress on this roadmap does not grant authority to mutate the system.

## Governing model

The intended flow is:

**human intent → AI reasoning → sanitized evidence → deterministic plan → human authorization where required → deterministic adapter execution → verification/rollback → durable project knowledge**

AI may help decide what to inspect, interpret evidence, synthesize a plan, or investigate a novel problem. Once a procedure is understood well enough to become routine, it should move out of model reasoning and into typed, tested, version-controlled Workbench data or code.

Agents and model providers remain replaceable. No capability may depend on one particular model, vendor, or hosted service.

## Safety and trust boundaries

AI capabilities must preserve the existing Workbench safety model.

- AI-generated plans are proposals, never authorization.
- Observed state is never silently promoted to desired state.
- Unknown or inaccessible evidence remains unknown rather than being inferred as absence.
- System mutation uses typed adapter operations, not arbitrary model-generated shell strings.
- Consequential changes remain bound to transaction-specific human authorization and fresh pre-state validation.
- AI cannot weaken, rewrite, or self-authorize around safety policy as part of a requested operation.
- Secrets, credentials, private histories, arbitrary user files, and broad home-directory contents stay outside AI context unless separately and explicitly authorized for a concrete purpose.
- Diagnostic collection should prefer narrow reviewed probes and sanitized evidence.
- Model conclusions must retain provenance: observed fact, documented capability, inference, hypothesis, and unknown should remain distinguishable.
- Reusable discoveries should be distilled into deterministic tests, adapters, mappings, recovery recipes, or machine-profile knowledge rather than left only in conversational memory.

## A0 — Agent foundation

**Status: substantially present.**

Workbench already establishes the architectural foundation:

- replaceable agents and providers;
- sanitized deterministic collection;
- inspect/compare/plan separation;
- explicit unknown states;
- repository-recorded discoveries;
- typed mutation transactions;
- exact authorization gates;
- backup/verify/rollback lifecycle.

The current Codex batch workflow is an early external form of agent orchestration, but it is not yet a first-class Workbench capability.

Exit criterion: the repository's safety and architecture rules remain the common substrate for every later AI capability.

## A1 — Explain and advise

Provide a conversational/read-only reasoning layer over Workbench evidence.

The first implemented substrate is `workbenchlib.explanation_evidence.build_bundle`.
It accepts explicit normalized snapshot, comparison, and proposal documents and
returns a JSON-serializable bundle with separate observations, changes, and
proposal sections. Probe status, unknown observations, and provenance are
retained. Missing sections are `null`; incomplete probe facts become unknown.
It performs no collection or model reasoning. This is evidence preparation,
not completion of A1 Explain/Advise or authority to apply a proposal.

The next deterministic substrate is
`workbenchlib.explanation_formatter.format_bundle`. It renders an explicit A1
evidence bundle as stable terminal text with separate known observations,
unknown/incomplete evidence, comparison changes, and proposal-only sections.
Facts and provenance remain uninterpreted data. This formatter performs no
collection or model reasoning and does not complete A1 Explain/Advise.

Representative user intents:

- “What changed since my last known-good state?”
- “Why does Workbench think this application is missing?”
- “What parts of my workstation differ from the desired profile?”
- “Explain this KDE compatibility block.”
- “What should I investigate next?”

The AI layer should consume normalized Workbench snapshots, comparisons, plans, review records, and adapter evidence rather than scraping arbitrary machine state itself.

Expected capabilities:

- explain normalized observations in human terms;
- summarize meaningful drift while suppressing noise;
- distinguish facts from inference;
- surface unknown or incomplete evidence;
- link conclusions back to the probe, adapter, review, or documentation that supports them;
- suggest a next read-only probe or planning action when evidence is insufficient.

Potential interface names such as `workbench explain` or `workbench ask` are illustrative, not yet commitments.

Mutation authority: none.

## A2 — Diagnostic investigator

Add bounded hypothesis-driven troubleshooting for unfamiliar failures.

A diagnostic session should have an explicit problem statement, evidence set, hypotheses, requested probes, findings, rejected hypotheses, and stopping condition. The agent may propose additional narrow probes, but new collection surfaces should be reviewed before becoming routine.

The investigator should support workflows such as:

- compare current state to a known-good snapshot;
- correlate kernel/package/desktop changes with the onset of a problem;
- identify what evidence would distinguish competing hypotheses;
- stop when evidence is insufficient instead of escalating into broad collection;
- produce a reusable investigation record.

The HP Envy B&O work is a useful manual precedent: diagnosis first, one controlled observation/change at a time, and durable recording of discoveries. Future Workbench diagnostics should formalize that pattern without pulling the audio research itself back into this repository.

Mutation authority: read-only by default. Any experiment that changes state becomes a separately reviewed Workbench transaction.

## A3 — Intent-to-plan synthesis

Allow users to describe desired outcomes without specifying implementation details.

Examples:

- “Use Super+1 through Super+4 for my four workspaces.”
- “Set this machine up for modern C++ development.”
- “Make this a good 3D-art workstation.”
- “Keep my application shortcuts familiar to a Windows user.”

The AI translates the request into portable Workbench intent, identifies relevant adapters, checks observed state, and synthesizes a deterministic candidate plan.

Requirements:

- preserve machine-independent intent separately from distro/desktop implementation;
- identify unresolved choices instead of silently inventing preferences;
- reuse existing desired-state and desktop-intent models;
- classify plan risk and required authorization boundary;
- never emit a mutation merely because a natural-language request sounds imperative;
- require the deterministic transaction layer for any consequential action.

This stage should also support composable environment profiles such as development, creative, office, gaming, or research roles without hard-wiring them to KDE or CachyOS.

Mutation authority: planning only until the normal Workbench authorization lifecycle is entered.

## A4 — Knowledge distillation

Make “we solved this once” a first-class lifecycle.

After an AI-assisted investigation succeeds, Workbench should identify what can be promoted into durable automation:

- a new or improved deterministic probe;
- an adapter compatibility rule;
- a desired-state mapping;
- a fixture/regression test;
- a recovery recipe;
- a machine-profile fact;
- a version-specific compatibility record;
- a documented unsupported/unknown boundary.

The AI may propose the distillation, but promotion requires review and tests. Raw conversations should not become executable knowledge automatically.

A useful success metric is decreasing model dependence over time: recurring tasks that once required investigation should eventually become normal deterministic Workbench operations.

Mutation authority: repository changes may be proposed/implemented under normal project rules; system mutation remains separately gated.

## A5 — Bounded agent work queues

Bring the successful batch workflow into Workbench as an explicit orchestration capability.

A queue should define:

- a bounded goal;
- ordered jobs;
- allowed evidence and tools;
- stop conditions;
- checkpoint expectations;
- tests/verification;
- hard human review gates.

The system should support long autonomous stretches for repository work and read-only investigation while stopping automatically at privacy, uncertainty, unsupported-interface, or mutation boundaries.

The queue is not a general permission slip. Individual jobs inherit AGENTS.md and transaction authorization rules. A queue must be unable to convert “complete these jobs” into permission for a live system change.

Potential future features include resumable queues, machine-readable checkpoint state, handoff between agents, and an operator-facing status summary.

Mutation authority: only through independently authorized Workbench transactions; queue execution itself grants none.

## A6 — Maintenance and update intelligence

Use AI to reason about drift caused by normal workstation evolution.

Examples:

- identify adapter assumptions invalidated by a KDE or kernel upgrade;
- explain why a previously valid transaction is now blocked;
- determine which compatibility probes/tests should be rerun after upgrades;
- flag stale package/application mappings;
- identify workarounds that may no longer be needed;
- summarize meaningful workstation health changes over time.

The KWin 6.7.5 D-Bus signature investigation is representative: version-specific evidence belongs in a compatibility record, and future versions should fail closed until revalidated rather than inheriting assumptions blindly.

This capability should eventually support periodic or user-triggered “what needs attention?” reviews without automatically repairing anything.

Mutation authority: advisory by default; remediation uses normal plans and authorization.

## A7 — Independent review and multi-agent workflows

Add optional second-agent review for high-complexity or high-risk work.

Possible patterns:

- planner agent proposes a diagnostic or transaction;
- reviewer agent critiques assumptions, evidence gaps, privacy exposure, rollback coverage, and version applicability;
- implementer agent works only from the reviewed artifact;
- verifier agent checks tests/results against the approved plan.

The roles should be logical rather than provider-specific. One provider may fill multiple roles, or different local/hosted models may be used.

This should be reserved for work where independent review adds value rather than imposed on every trivial operation.

Mutation authority: reviewer consensus never substitutes for human authorization where the safety model requires it.

## A8 — Provider and model routing

Allow Workbench to select among available agents/models based on capability, privacy, cost, latency, and task type without changing workstation semantics.

Possible policy dimensions:

- local versus hosted execution;
- read-only summarization versus deep technical investigation;
- context sensitivity/privacy;
- expected reasoning difficulty;
- code-generation capability;
- independent-review diversity;
- offline availability.

Provider routing must be policy-driven and inspectable. Workbench should function with a minimal single-agent setup and gain optional capabilities when additional providers are available.

No secret/API-key management should be embedded in repository data. Provider credentials remain outside version-controlled Workbench state.

Mutation authority: none by itself.

## Suggested implementation order

The near-term order should favor capabilities that add intelligence without broadening system authority:

**A1 Explain/Advise → A2 Diagnostic Investigator → A4 Knowledge Distillation → A3 Intent-to-Plan → A5 Agent Queues → A6 Maintenance Intelligence → A7 Multi-Agent Review → A8 Provider Routing**

A3 and A5 may move earlier if concrete workflows justify them. A6 becomes substantially more valuable once Workbench has several operational adapters and a history of successful controlled mutations.

Batch 005 being deferred does not block A1, A2, A4, or much of A3/A5 because those can remain read-only or repository-scoped.

## Non-goals

Workbench should not become:

- an unrestricted natural-language root shell;
- a model that continuously watches arbitrary private user activity;
- a system that silently changes desired state based on what it observes;
- an agent that automatically installs/removes/configures things because it predicts user preference;
- a replacement for deterministic package/configuration tooling once a procedure is understood;
- dependent on permanent cloud connectivity or a single AI provider;
- a self-modifying safety policy.

The core product idea remains a **deterministic workstation manager with an intelligent reasoning layer**, not an autonomous model with a shell.
