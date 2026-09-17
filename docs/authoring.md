# Author an extension

An extension maps model-visible arguments onto an existing app interface. EVA parses
the file, previews its destinations and effects, and runs it only after the user
enables it. You do not add Kotlin, JavaScript, a service, or a registration entry
to either app.

## Choose an interface

| Interface | Use it for | Current Android support |
| --- | --- | --- |
| `android.intent` | Documented deep links or exported activities with scalar extras | Implemented; Caffeine and Messages device-tested |
| `http` | An existing HTTPS JSON API | Implemented and JVM-tested; examples not device-verified |
| `android.content` | Read-only content-provider queries with typed URI slots | Implemented and Robolectric-tested; Mova/Paseo device verification pending |
| `packageByName` on an intent | Choose a target using a visible app name | Parsed, but Android execution unavailable |

An intent is an **activity launch**, not a broadcast or service call. Check the
target app's documentation for the exact action, URI, activity class, and extra
types. A private activity cannot be made accessible by a package file. Android
permissions, export rules, and background-launch restrictions still apply.

A successful launch proves only `HANDED_OFF`. It cannot prove a message was
sent, a todo was created, or a setting changed. If you need a confirmed result,
use an interface that returns evidence. The Messages extension intentionally opens
a draft; declaring it a write does not turn it into direct SMS sending.

## Start with one action

This is a complete package. It asks an installed map handler to search a place:

```json
{
  "formatVersion": 1,
  "id": "community.map-search",
  "version": "0.1.0",
  "title": "Map search",
  "androidPackages": [],
  "capabilities": [
    {
      "tool": {
        "name": "search",
        "title": "Search maps",
        "description": "Open a map search for a place. Reports handoff, not arrival or navigation completion.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "place": {"type": "string", "minLength": 1, "maxLength": 500}
          },
          "required": ["place"],
          "additionalProperties": false
        }
      },
      "effects": "external_handoff",
      "execution": {
        "mode": "handoff",
        "requiresForeground": true
      },
      "binding": {
        "kind": "android.intent",
        "action": "android.intent.action.VIEW",
        "uri": {
          "base": "geo:0,0",
          "query": {"q": {"argument": "place", "type": "string"}}
        }
      }
    }
  ]
}
```

The `tool` object is the MCP tool description of the action, including its
`title`; it may also carry `outputSchema` and `annotations` (see the
[reference](package-format.md)).
The `binding` fixes what it can do. Arguments fill typed, encoded slots; they cannot
choose an arbitrary action, component, origin, or shell command.

For a fixed activity and integer extras, copy [Caffeine](../packages/caffeine.json).
For opaque URI data and a named validator, see [Messages](../packages/messages.json).
For HTTP nested body mappings and item projections, see
[HTTP notes](examples/http-notes.json).
For reads that discover IDs for intent actions in the same package, see
[Mova](../packages/mova.json) and [Paseo](../packages/paseo.json). Content queries return only declared
columns, with row/byte limits and no partial rows. Use typed URI query/path slots
for providers that take URL parameters; SQL selection is a different interface.

Content visibility and Android permissions must already be supported by EVA's
installed manifest. EVA explicitly queries the Mova and Paseo provider
authorities and offers Mova's runtime read-permission request from extension
settings. JSON cannot add authorities to Android's visibility declarations or
request arbitrary permissions. See the [content reference](package-format.md#content-binding)
before targeting another provider.

## Describe effects and outcomes honestly

Declare `read`, `write`, `external_handoff`, or `unknown`. Omission means
unknown. EVA applies a minimum effect for each binding and treats all non-read
effects as requiring a write grant. Package prose cannot weaken that policy.

Descriptions should state what the action does, prerequisites, and what its
receipt can establish. Include identifiers in read results if a later action
needs them. Optional `receipts.success` and `receipts.handlerMissing` are fixed
display text, not templates or evidence.

There is no `enabledByDefault` or per-capability default-grant field. Reads
follow extension enablement; users approve other actions. Grants persist for an
unchanged contract. An update with changed canonical content requires
re-enablement, even if only descriptive text changed.

## Test locally, then publish

1. Save the complete JSON file. Use valid JSON without comments or trailing commas.
2. Import it through **Extensions → Browse → Import extension file**.
3. Inspect the preview. A parse/validation error means nothing was installed.
4. Install, enable the extension, and expand it to grant the actions you will test.
5. For HTTP, configure the named credential and approved server origin under
   **Extensions → Settings**. Keep secrets out of the file. For content reads,
   expand the installed package, check provider availability, and use **Allow
   provider reads** when Android permission is required. Authorize each device
   separately after restoring configuration.
6. Reconnect in typed mode. Ask for exactly one action and inspect its receipt.
   Test missing inputs, special characters, missing target apps, and failure cases.
   Test writes only against data you intend to change.
7. Check the target app/server independently. Do not infer completion from model prose.
8. Add the file to `packages/`, bump its version when replacing a published
   definition, then commit and publish the package as described in [repositories](repositories.md).

File reimports create separate instances. For testing updates rather than fresh
installs, use a stable catalog repository or raw HTTPS package URL.

Timeouts after submission mean `UNKNOWN`, not cancellation. Check the target
before retrying a write. An imported mutation following a tool result needs a
separate user request; “search then complete” should be two requests in this version.

APIs without server search can use the local `items.filter` primitive shown in
[HTTP notes](examples/http-notes.json). That searches only returned data; it does
not fetch missing pages or provide strict write semantics to an older server.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| “Unexpected or missing fields” | Exact names and required fields in the [reference](package-format.md); unknown keys are rejected |
| Preview fails for a GitHub URL | Use `raw.githubusercontent.com`, not a `github.com/.../blob/...` page |
| Repository does not refresh | Confirm the HTTPS Git URL clones anonymously and that `packages/*.json` files decode; the refresh notice names files that were skipped |
| Changed package cannot install | Increase `version`; changed content at the same version and downgrades are refused |
| Extension visible but model cannot use it | Enable/grant, reconnect, and check catalog overflow/availability |
| App not detected | Matching depends on Android visibility; try manual import and check actual intent handling |
| Activity unavailable | Install/enable the app, confirm exported activity and exact package/class for that version |
| Content action unavailable | Use an EVA build with content execution; install/enable the provider app, check authority visibility, and grant its read permission in extension settings |
| Content read fails | Verify exact projection columns/types and provider-supported query/selection parameters; null cursors and invalid columns fail without partial rows |
| App-name action unavailable | `packageByName` is parsed but not yet implemented by the Android host |
| HTTP credential missing | Match the reference name and approved origin; no paths or credentials in the origin |
| HTTP read is unknown | Check JSON shape/types, response limit, deadline, and HTTP 202 |
| HTTP write is unknown | Require real terminal evidence; a 2xx response alone is insufficient |
