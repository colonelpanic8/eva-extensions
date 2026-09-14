# EVA plugins

Declarative JSON plugins for EVA. Updating this repository can add capabilities
without rebuilding EVA or modifying a target app, within EVA's supported bindings.

In EVA, open Extensions, enter the raw HTTPS URL of `index.json`, refresh,
preview a package, and install it. Then enable the extension and approve each
write action separately. Reconnect the conversation to use newly enabled actions.

- Caffeine: enable/disable keep-awake in the existing Android app.
- Messages: open an unsent SMS draft in the phone's messaging app.
- Org agenda: HTTP example requiring an approved server and a named credential.
  Search and strict completion need the documented compatible server deployment.

Each package is self-contained. No credentials or executable scripts belong here.
Increase its three-part version for changed content, then run
`python3 update-index.py`. Commit the JSON and generated index together.
Index hashes cover exact file bytes. EVA previews updates and invalidates grants
when approved content changes. Package IDs do not authenticate publishers.

This checkout is prepared locally; it has not been published to GitHub.
