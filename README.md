# EVA plugins

JSON packages that teach [EVA](https://github.com/colonelpanic8/eva) how to use
existing Android apps and HTTP APIs. A new package can add actions without an EVA
release or target-app changes, provided the app exposes a supported interface.
Packages contain data, never executable code.

## Install a plugin

This repository is EVA's default catalog. In EVA, open **Extensions → Browse**
and select **Refresh available extensions**; EVA keeps a read-only clone of

```text
https://github.com/colonelpanic8/eva-extensions.git
```

and lists every package under `packages/`. Preview and install a package, then enable it in **Installed**. Expand its row to
grant individual write actions. Reads are enabled with the plugin; writes and
unknown effects require separate approval. Reconnect your conversation to expose
new actions to the model. Refreshing the repository alone does not install updates.

Browse also accepts a raw HTTPS package URL or a JSON file through **Import plugin
file**. Use raw file URLs, not GitHub's HTML “blob” pages.

## Write a plugin

Start with the [authoring guide](docs/authoring.md), then use the
[complete v1 format reference](docs/package-format.md). The
[repository and update guide](docs/repositories.md) explains catalog repositories,
app matching, versioning, and publishing your own.

| Package | What it does | Verification |
| --- | --- | --- |
| [Caffeine](packages/caffeine.json) | Enable/disable keep-awake through a fixed activity | Typed handoff and notification changes verified on Pixel |
| [Calendar](packages/calendar.json) | Open a prefilled new event in the calendar app | Codec decode and intent construction verified by EVA's JVM tests; device test pending. EVA installs this package by default |
| [Email](packages/email.json) | Open an addressed email draft with optional subject and body | Codec decode and intent construction verified by EVA's JVM tests; device test pending. EVA installs this package by default |
| [Google Maps](packages/google-maps.json) | Search the map through `geo:` and start turn-by-turn navigation by travel mode through `google.navigation:` | Codec decode and intent construction verified by EVA's JVM tests; device test pending. EVA installs this package by default |
| [Messages](packages/messages.json) | Open an addressed, unsent SMS draft | Typed handoff verified on Pixel; does not send |
| [Mova](packages/mova.json) | Discover templates, todos and agenda rows; create and manage todos through Mova's Android intents | All 15 capabilities verified with EVA Debug and Mova 7.0.1 on a Pixel 11 Pro Fold |
| [Settings](packages/settings.json) | Open a named settings screen through Android's settings actions | Codec decode and intent construction verified by EVA's JVM tests; device test pending. EVA installs this package by default |
| [Web](packages/web.json) | Web search, and open an http or https page | Codec decode and intent construction verified by EVA's JVM tests; device test pending. EVA installs this package by default |
| [Paseo](packages/paseo.json) | List workspaces and agents through Paseo's content provider; open them and draft or send prompts through `paseo://` links | Schema and codec decode verified against Paseo's `android-intents` branch and EVA's `content-provider-execution` branch; device test deferred |

An additional [HTTP authoring example](docs/examples/http-notes.json) demonstrates
local filtering and write evidence against a hypothetical API; it is outside the
installable `packages/` directory.

The Web, Email, Calendar, and Settings packages are EVA's stock Android actions
expressed as data; see their [interface notes](docs/stock-android.md).

The Google Maps package uses the vendor-neutral `geo:` scheme for search and
Google's documented `google.navigation:` intent for navigation. See its
[interface and verification notes](docs/google-maps.md).

The Mova package targets the Android app rather than the org-agenda HTTP API.
See its [read, action and permission setup notes](docs/mova.md). Reads require an
EVA build with content execution and Mova's Android read grant. Updating the
package to 0.2.1 requires re-enablement and renewed action grants.

The Paseo package drives the coding-agent app's `paseo://` links. See its
[draft-versus-send and host resolution notes](docs/paseo.md).

These documents describe the declarative package protocol. EVA's separate
installed-service AIDL protocol (in EVA’s `docs/extension-protocol.md`)
requires code in the target app and is not needed for these plugins.
AppFunctions is another adapter, not a binding kind in these JSON files.

## Contribute

Keep each plugin in one `packages/<name>.json` file and increase its three-part
version when content changes; there is no index to regenerate. Validate through
EVA's preview and test the actual action before claiming device support. Never
commit credentials.

Format documentation was checked against EVA
`000f95f`, which implements content-provider execution and typed content URI slots.
Availability notes distinguish parser support from Android execution support.
