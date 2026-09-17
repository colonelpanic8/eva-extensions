# EVA extensions

JSON packages that teach [EVA](https://github.com/colonelpanic8/eva) how to use
existing Android apps and HTTP APIs. A new package can add actions without an EVA
release or target-app changes, provided the app exposes a supported interface.
Packages contain data, never executable code.

## Install an extension

This repository is EVA's default catalog. In EVA, open **Extensions → Browse**
and select **Refresh available extensions**; EVA keeps a read-only clone of

```text
https://github.com/colonelpanic8/eva-extensions.git
```

and lists every package under `packages/`. Preview and install a package, then enable it in **Installed**. Expand its row to
grant individual write actions. Reads are enabled with the extension; writes and
unknown effects require separate approval. Reconnect your conversation to expose
new actions to the model. Refreshing the repository alone does not install updates.

Browse also accepts a raw HTTPS package URL or a JSON file through **Import
extension file**. Use raw file URLs, not GitHub's HTML “blob” pages.

## Write an extension

Start with the [authoring guide](docs/authoring.md), then use the
[complete v1 format reference](docs/package-format.md). The
[repository and update guide](docs/repositories.md) explains catalog repositories,
app matching, versioning, and publishing your own.

An extension documents itself: its `description` and `setup` say what it is for
and what the user must do outside EVA, and each capability's `description` states
what that action does and what its result proves. EVA shows all of it before the
user installs, and hands the capability descriptions to the model, so this file
records only what a package cannot claim about itself.

| Extension | What it does | Verification |
| --- | --- | --- |
| [Caffeine](packages/caffeine.json) | Enable/disable keep-awake through a fixed activity | Typed handoff and notification changes verified on Pixel |
| [Clock](packages/clock.json) | Set alarms and start countdown timers through Android's standard clock app intents | Intent shape mirrors EVA's native alarm/timer adapters; device test pending |
| [Calendar](packages/calendar.json) | Open a prefilled new event in the calendar app | Codec decode and intent construction verified by EVA's JVM tests; device test pending. Installed by default |
| [Email](packages/email.json) | Open an addressed email draft with optional subject and body | Codec decode and intent construction verified by EVA's JVM tests; device test pending. Installed by default |
| [Google Maps](packages/google-maps.json) | Search the map through `geo:` and start turn-by-turn navigation by travel mode through `google.navigation:` | Codec decode and intent construction verified by EVA's JVM tests; device test pending. Installed by default |
| [Google Translate](packages/google-translate.json) | Open Live translate for a spoken conversation, with the source and target languages set from the request | Package decode and intent construction checked against EVA's codec; the link, its `sl`/`tl` languages and its live-mode flag are the ones Google Translate 10.35 builds for its own Live translate shortcut; device test pending |
| [Messages](packages/messages.json) | Open an addressed, unsent SMS draft | Typed handoff verified on Pixel; does not send |
| [Mova](packages/mova.json) | Discover templates, todos and agenda rows; create and manage todos through Mova's Android intents | All 15 capabilities verified with EVA Debug and Mova 7.0.1 on a Pixel 11 Pro Fold; the 0.3.0 prompt map and decoded template prompts are JVM-tested only |
| [Settings](packages/settings.json) | Open a named settings screen through Android's settings actions | Codec decode and intent construction verified by EVA's JVM tests; device test pending. Installed by default |
| [Web](packages/web.json) | Web search, and open an http or https page | Codec decode and intent construction verified by EVA's JVM tests; device test pending. Installed by default |
| [Paseo](packages/paseo.json) | List workspaces and agents through Paseo's content provider; open them and draft or send prompts through `paseo://` links | Schema and codec decode verified against Paseo's `android-intents` branch; device test deferred |

An additional [HTTP authoring example](docs/examples/http-notes.json) demonstrates
local filtering and write evidence against a hypothetical API; it is outside the
installable `packages/` directory.

These documents describe the declarative package protocol. EVA's separate
installed-service AIDL protocol (in EVA’s `docs/extension-protocol.md`)
requires code in the target app and is not needed for these extensions.
AppFunctions is another adapter, not a binding kind in these JSON files.

## Contribute

Keep each extension in one `packages/<name>.json` file and increase its three-part
version when content changes; there is no index to regenerate. Put what the
extension is and needs in its own `description` and `setup`, not in a separate
document. Validate through EVA's preview and test the actual action before
claiming device support here. Never commit credentials.

Format documentation was checked against EVA
`000f95f`, which implements content-provider execution and typed content URI slots.
Availability notes distinguish parser support from Android execution support.
