# KDE feasibility evidence contract

`adapters.kde_feasibility.collect()` returns only fixed IDs, evidence type,
status, and normalized values. Its current local probes check fixed tool names
and read the exact `kwinrc` `Desktops/Number` key through `kreadconfig6`.
The latter accepts only an integer from 1 to 20. Malformed, inaccessible,
missing, or failed observations are unknown. Command output and stderr never
enter the returned evidence. No D-Bus method is used; additional D-Bus reads
require a reviewed exact interface, property, and parser before inclusion.

`official_documentation` means a linked KDE capability claim with version
applicability. `local_observation` means a successfully parsed read-only probe.
`project_inference` means a recommendation derived from those facts. `unknown`
means the safe evidence does not establish the claim. A tool check says only
that the executable is available in PATH; it does not prove a configured
capability. Existing `plasma_version` and `kwin_version` collector probes
remain the authoritative local version observations. This catalog neither
reads private desktop state nor changes Plasma/KWin.
