# EVA plugins

JSON packages that teach [EVA](https://github.com/colonelpanic8/eva) how to use
existing Android apps and HTTP APIs. A new package can add actions without an EVA
release or target-app changes, provided the app exposes a supported interface.
Packages contain data, never executable code.

## Install a plugin

In EVA, open **Extensions → Browse**, enter this repository URL, and select
**Refresh plugin repository**:

```text
https://raw.githubusercontent.com/colonelpanic8/eva-plugins/main/index.json
```

Preview and install a package, then enable it in **Installed**. Expand its row to
grant individual write actions. Reads are enabled with the plugin; writes and
unknown effects require separate approval. Reconnect your conversation to expose
new actions to the model. Refreshing the repository alone does not install updates.

Browse also accepts a raw HTTPS package URL or a JSON file through **Import plugin
file**. Use raw file URLs, not GitHub's HTML “blob” pages.

## Write a plugin

Start with the [authoring guide](docs/authoring.md), then use the
[complete v1 format reference](docs/package-format.md). The
[repository and update guide](docs/repositories.md) explains indexes, hashes,
app matching, versioning, and publishing your own repository.

| Package | What it does | Verification |
| --- | --- | --- |
| [Caffeine](packages/caffeine.json) | Enable/disable keep-awake through a fixed activity | Typed handoff and notification changes verified on Pixel |
| [Messages](packages/messages.json) | Open an addressed, unsent SMS draft | Typed handoff verified on Pixel; does not send |
| [Org agenda](packages/org-agenda.json) | Read/search/capture/complete through an HTTP API, plus a mova deep link | JVM-tested; server deployment/device test deferred |

The org-agenda example requires its documented `q`/`limit`/`total` and strict
completion API. See [its prerequisites](docs/authoring.md#org-agenda-prerequisites).
An additional [HTTP authoring example](docs/examples/http-notes.json) demonstrates
local filtering and write evidence against a hypothetical API; it is not listed
in the installable index.

These documents describe the declarative package protocol. EVA's separate
installed-service AIDL protocol (in EVA’s `docs/extension-protocol.md`)
requires code in the target app and is not needed for these plugins.
AppFunctions is another adapter, not a binding kind in these JSON files.

## Contribute

Keep each plugin in one `packages/<name>.json` file. Increase its three-part
version when content changes, run `python3 update-index.py`, and commit the file
and generated index together. The generator creates hashes; it is **not** a
package-schema validator. Validate through EVA's preview and test the actual
action before claiming device support. Never commit credentials.

Format documentation was checked against EVA
`32e8e14` (2026-09-14).
Availability notes distinguish parser support from Android execution support.
