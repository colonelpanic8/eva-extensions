# EVA plugins

JSON packages that teach [EVA](https://github.com/colonelpanic8/eva) how to use
existing Android apps and HTTP APIs. A new package can add actions without an EVA
release or target-app changes, provided the app exposes a supported interface.
Packages contain data, never executable code.

## Install a plugin

In EVA, open **Extensions → Browse**, enter this Git repository URL, and select
**Refresh plugin repository**:

```text
https://github.com/colonelpanic8/eva-plugins.git
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
[repository and update guide](docs/repositories.md) explains repository layout,
app matching, versioning, and publishing your own repository.

| Package | What it does | Verification |
| --- | --- | --- |
| [Caffeine](packages/caffeine.json) | Enable/disable keep-awake through a fixed activity | Typed handoff and notification changes verified on Pixel |
| [Messages](packages/messages.json) | Open an addressed, unsent SMS draft | Typed handoff verified on Pixel; does not send |
| [Mova](packages/mova.json) | Create and manage todos through Mova's Android intents | Format and intent construction verified against Mova 7.0.1; device test deferred |

An additional [HTTP authoring example](docs/examples/http-notes.json) demonstrates
local filtering and write evidence against a hypothetical API; it is outside the
installable `packages/` directory.

The Mova package targets the Android app rather than the org-agenda HTTP API.
See its [supported action and ContentProvider notes](docs/mova.md), including why
provider-backed template and todo reads are not exposed by the current package.

These documents describe the declarative package protocol. EVA's separate
installed-service AIDL protocol (in EVA’s `docs/extension-protocol.md`)
requires code in the target app and is not needed for these plugins.
AppFunctions is another adapter, not a binding kind in these JSON files.

## Contribute

Keep each plugin in one `packages/<name>.json` file. Increase its three-part
version when content changes and commit that file. Validate through EVA's preview
and test the actual action before claiming device support. Never commit credentials.

Format documentation was checked against EVA
`8a0d4e2` (2026-09-14).
Availability notes distinguish parser support from Android execution support.
