# Batch 004B read-only preflight blocker

Date: 2026-09-29. The production workspace pilot remains blocked before
authorization. No live mutation was attempted.

The final read-only `./workbench workspace-pilot preflight` checked the
`org.kde.KWin.VirtualDesktopManager` session interface on KWin 6.7.5.
Introspection and the installed interface XML declare the ordered `desktops`
property as `a(iss)`, while the live property reply reports `a(uss)`. The
fixed-version backend rejects this signature mismatch. The interface XML also
confirms that `createDesktop(us)` has no return value; the backend was
corrected to require that exact method signature.

The preflight stopped before reading a complete runtime/config pre-state and
before constructing a new fingerprint. The Batch 004 fingerprint
`67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963`
cannot be classified as matching or drifted by this preflight. Its review
does not authorize any live action.

Further source-backed investigation must resolve whether the live reply's
signature is a KWin defect, a `busctl` presentation issue, or a distinct
runtime interface before any production executor can be used. Do not relax
the version/interface guard, issue an authorization, or invoke live apply or
rollback on this evidence. The remaining Batch 004B jobs stop at this
blocker under the handoff's explicit stop condition.
