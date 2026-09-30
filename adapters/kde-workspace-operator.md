# Four-workspace operator CLI

`./workbench workspace-pilot preflight` reads the session KWin 6.7.5 desktop
interface and allowlisted `Desktops` keys. Its fingerprint describes the
current exact plan; generating it is not authorization. Review its sanitized
result before any future approval. Private desktop IDs, names, and config
values stay out of command output.

Only after separate explicit human approval of the exact transaction and
fingerprint, an operator can run these distinct commands in the KDE user
session:

```text
./workbench workspace-pilot authorize <reviewed-fingerprint>
./workbench workspace-pilot apply <reviewed-fingerprint>
./workbench workspace-pilot verify
./workbench workspace-pilot rollback kde-four-workspaces-v1
```

`authorize` requires an interactive terminal entry of both the transaction
ID and fingerprint and creates a single-use authorization in ignored local
storage. It expires after 15 minutes. `apply` repeats the exact version,
interface, plan, and pre-state checks, consumes the authorization, takes the
narrow backup, rechecks pre-state, and applies the four typed actions. It
verifies after each action and independently verifies runtime and config at
the end. On failure after mutation begins, it attempts and verifies rollback.
The backup remains under `.workbench/backups/` for explicit recovery. The
rollback command accepts only the matching pilot backup ID from the private
run record and refuses a changed runtime state.

No live authorization, apply, or rollback command is permitted by Batch 004B.
