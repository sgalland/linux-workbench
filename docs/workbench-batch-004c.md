# Workbench Batch 004C — KWin D-Bus Signature Reconciliation + Preflight Resume

Purpose: resolve the Batch 004B KWin 6.7.5 VirtualDesktopManager signature blocker using exact-version source evidence, update the live backend without weakening its version/interface guard, rerun the read-only preflight, and return to a fresh human authorization gate.

This is a narrow continuation of Batch 004B. It does not authorize or execute any live desktop mutation.

Complete jobs in order, make one clean checkpoint commit after each job, continue automatically while tests remain green, and stop at the final review gate.

## Global rules

- Read AGENTS.md, docs/safety-model.md, docs/workbench-batch-004b.md, docs/reviews/workbench-batch-004b-interface-blocker.md, adapters/kde_live.py, adapters/kde-workspace-mutation.md, and adapters/kde-workspace-operator.md first.
- No sudo, package changes, service changes, KWin/Plasma restart, or unrelated desktop/system changes.
- Do not run live authorize, apply, or rollback.
- The only permitted live-session operation is the final read-only preflight and any narrowly scoped read-only evidence checks required to validate the exact interface.
- Do not weaken the backend into “accept either a(iss) or a(uss)”.
- Do not generalize this exception beyond the exact source-verified KWin version/interface case.
- Preserve all existing transaction, authorization, backup, lock, drift, and rollback protections.
- Do not touch machines/hp-envy/experimental-kernel/.

## Source-verified discrepancy

For KWin v6.7.5, the checked-in D-Bus XML declares:

- property desktops: a(iss)

But the exact-version C++ implementation declares:

- DBusDesktopDataStruct.position as uint
- id as QString
- name as QString

and the marshaller writes those fields in that order. Therefore the actual runtime wire structure is:

- (uss)
- desktops property wire reply: a(uss)

Treat this as a specific metadata/source discrepancy in KWin 6.7.5, not as permission to ignore interface mismatches generally.

Relevant exact-version sources:
- src/virtualdesktopsdbustypes.h
- src/virtualdesktopsdbustypes.cpp
- src/org.kde.KWin.VirtualDesktopManager.xml

Record these in the repository with links/version applicability. Distinguish:
- declared introspection/XML signature: a(iss)
- source-defined runtime struct/wire signature: a(uss)
- locally observed runtime reply: a(uss)

## Job 1 — Evidence record and compatibility rule

Create a concise adapter evidence record for the KWin 6.7.5 signedness discrepancy.

The rule must be explicit:

For exactly KWin 6.7.5 and exactly org.kde.KWin.VirtualDesktopManager.desktops:
- require introspection/XML to advertise a(iss);
- require the live property reply to be a(uss);
- require the remaining method/property surface to match the reviewed exact interface;
- require desktop position values to be non-negative integers forming the exact contiguous ordering expected by the backend.

Any different version, different introspection signature, different runtime signature, missing member, extra incompatible member, or malformed payload must fail closed.

Do not encode a fallback that accepts whichever signature happens to appear.

Update the Batch 004B blocker record to point to this source-backed resolution path while preserving that the original stop was correct.

Checkpoint commit.

## Job 2 — Backend reconciliation and regression tests

Update adapters/kde_live.py so its exact-version validation distinguishes the declared XML/introspection signature from the source-verified runtime property signature.

Expected behavior for KWin 6.7.5:
- validate_surface() still requires desktops introspection signature a(iss);
- inspect() requires the live busctl property reply type a(uss);
- count/rows remain u;
- current remains s;
- createDesktop remains input us with no return value;
- setDesktopName remains ss with no return value;
- removeDesktop remains s with no return value.

Retain strict field validation:
- position must be an integer >= 0;
- position ordering must be exactly 0..count-1;
- id/name must be strings;
- count must equal row count;
- current must match an observed desktop ID through the existing State validation.

Add regression tests covering:
- exact expected a(iss) introspection + a(uss) live reply succeeds;
- a(iss) live reply fails for 6.7.5;
- any other live reply signature fails;
- changed introspection signature fails;
- signed/negative position fails;
- non-contiguous ordering fails;
- changed KWin version fails;
- missing/changed method/property fails.

Do not call live mutators.

Checkpoint commit.

## Job 3 — Re-run the complete safety suite

Run the complete automated suite, including all Batch 004/004B lifecycle, authorization, backup, failure-injection, concurrency, interruption, drift, and rollback tests.

Add any targeted regression test needed to prove that resolving the signature discrepancy did not weaken:
- stale-state rejection;
- transaction fingerprint binding;
- one-time authorization;
- version/interface guards;
- live mutation refusal without authorization;
- matching-backup rollback scope.

Run git diff --check.

If any guard must be weakened to make the preflight pass, stop and report the blocker instead of continuing.

Checkpoint commit.

## Job 4 — Fresh live read-only preflight

Run only:

    ./workbench workspace-pilot preflight

in the normal KDE user session.

Do not authorize or apply.

The preflight must:
- confirm KWin 6.7.5;
- confirm the exact declared introspection surface;
- confirm the exact source-verified a(uss) runtime desktop property reply;
- inspect the narrow runtime/config pre-state;
- generate a new transaction fingerprint;
- report only sanitized public fields.

Compare the new fingerprint to the Batch 004 reviewed fingerprint:

67b55bbe399a0eee08843d5b2ae86b83c95da3651c0a1c9f4bc0232e5b9d7963

A mismatch is not automatically an error because the executor/fingerprint material may have evolved. Classify why it differs without exposing private values.

Create docs/reviews/workbench-batch-004c-workspace-pilot.md containing:
- transaction ID;
- fresh fingerprint;
- whether it matches or differs from Batch 004;
- safe reason classification for any difference;
- KWin version/interface validation result;
- exact logical target: Development, General, Office, Creative;
- backup scope names only;
- verification sequence;
- rollback sequence;
- operator commands that would follow future explicit approval;
- remaining live risks.

Do not issue production authorization.

Checkpoint commit.

## Job 5 — Batch 004C review and human authorization stop gate

Create docs/reviews/workbench-batch-004c-review.md with:
- checkpoint commits;
- complete test count/results;
- exact source evidence for the a(iss) vs a(uss) discrepancy;
- final exact-version compatibility rule;
- regression-test results;
- fresh live preflight result;
- new fingerprint;
- whether the reviewed plan changed materially;
- remaining risks;
- exact next operator sequence after explicit human approval;
- confirmation that no production authorization was issued and no live mutation occurred.

Update docs/reviews/workbench-batch-004b-interface-blocker.md only enough to mark the blocker as source-resolved by 004C; do not erase the historical stop condition.

Stop here.

Do not run:
- ./workbench workspace-pilot authorize
- ./workbench workspace-pilot apply
- ./workbench workspace-pilot rollback

Do not interpret this batch request as approval of the pilot.

## Expected checkpoint sequence

1. source evidence + exact compatibility rule
2. backend reconciliation + regression tests
3. complete safety-suite verification
4. fresh live read-only preflight
5. Batch 004C review + human authorization stop gate

If the fresh runtime behavior differs from the exact KWin 6.7.5 source-backed rule above, stop immediately and report the new blocker rather than broadening compatibility.
