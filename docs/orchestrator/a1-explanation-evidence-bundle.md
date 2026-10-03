# A1 explanation evidence bundle

Implement the first deterministic substrate for the Linux Workbench A1 Explain/Advise capability.

Requirements:

- Add a read-only, provider-neutral explanation evidence bundle in `workbenchlib`.
- Build the bundle only from already-normalized Workbench data supplied to it; do not probe the live system, inspect arbitrary user files, or invoke shell commands.
- Do not call ChatGPT, Codex, another model, or any external AI provider.
- Do not mutate workstation state, desired state, repository configuration, or authorization state.
- Preserve distinctions between observed facts, unknown/incomplete evidence, proposed/planning information, and provenance/source information.
- Unknown or inaccessible evidence must remain unknown and must never be converted to absence or a guessed fact.
- Output must be deterministic and JSON-serializable.
- Use stable ordering so equivalent input produces equivalent output.
- Reuse existing Workbench schemas/data structures where practical instead of inventing parallel representations.
- Add focused unit tests for deterministic output, unknown preservation, provenance retention, and malformed or incomplete input.
- If a small CLI inspection surface fits the existing architecture cleanly, it may be added, but it must remain read-only and consume explicit existing/synthetic input rather than collecting new machine state.
- Update documentation only as needed to describe the substrate. Do not claim A1 Explain/Advise is complete and do not broaden any mutation authority.
- Keep the implementation intentionally small; this slice prepares evidence for future reasoning but does not implement model-backed explanations.
