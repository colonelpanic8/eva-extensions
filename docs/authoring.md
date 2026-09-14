# Author a plugin

A plugin maps model-visible arguments onto an existing app interface. EVA parses
the file, previews its destinations and effects, and runs it only after the user
enables it. You do not add Kotlin, JavaScript, a service, or a registration entry
to either app.

## Choose an interface

| Interface | Use it for | Current Android support |
| --- | --- | --- |
| `android.intent` | Documented deep links or exported activities with scalar extras | Implemented; Caffeine and Messages device-tested |
| `http` | An existing HTTPS JSON API | Implemented and JVM-tested; examples not device-verified |
| `android.content` | Read-only content-provider queries | Format/interpreter tested; Android execution unavailable |
| `packageByName` on an intent | Choose a target using a visible app name | Parsed, but Android execution unavailable |

An intent is an **activity launch**, not a broadcast or service call. Check the
target app's documentation for the exact action, URI, activity class, and extra
types. A private activity cannot be made accessible by a package file. Android
permissions, export rules, and background-launch restrictions still apply.

A successful launch proves only `HANDED_OFF`. It cannot prove a message was
sent, a todo was created, or a setting changed. If you need a confirmed result,
use an interface that returns evidence. The Messages plugin intentionally opens
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
      "title": "Search maps",
      "effects": "external_handoff",
      "execution": {
        "mode": "handoff",
        "requiresForeground": true,
        "cancellation": "none",
        "idempotency": "none",
        "reconciliation": "none"
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

The `tool` object is the MCP-compatible description of the action. The
`binding` fixes what it can do. Arguments fill typed, encoded slots; they cannot
choose an arbitrary action, component, origin, or shell command.

For a fixed activity and integer extras, copy [Caffeine](../packages/caffeine.json).
For opaque URI data and a named validator, see [Messages](../packages/messages.json).
For HTTP nested body mappings, conditional routes, and item projections, see
[HTTP notes](examples/http-notes.json) and [org agenda](../packages/org-agenda.json).

## Describe effects and outcomes honestly

Declare `read`, `write`, `external_handoff`, or `unknown`. Omission means
unknown. EVA applies a minimum effect for each binding and treats all non-read
effects as requiring a write grant. Package prose cannot weaken that policy.

Descriptions should state what the action does, prerequisites, and what its
receipt can establish. Include identifiers in read results if a later action
needs them. Optional `receipts.success` and `receipts.handlerMissing` are fixed
display text, not templates or evidence.

There is no `enabledByDefault` or per-capability default-grant field. Reads
follow plugin enablement; users approve other actions. Grants persist for an
unchanged contract. An update with changed canonical content requires
re-enablement, even if only descriptive text changed.

## Test locally, then publish

1. Save the complete JSON file. Use valid JSON without comments or trailing commas.
2. Import it through **Extensions → Browse → Import plugin file**.
3. Inspect the preview. A parse/validation error means nothing was installed.
4. Install, enable the plugin, and expand it to grant the actions you will test.
5. For HTTP, configure the named credential and approved server origin under
   **Extensions → Settings**. Keep secrets out of the file.
6. Reconnect in typed mode. Ask for exactly one action and inspect its receipt.
   Test missing inputs, special characters, missing target apps, and failure cases.
   Test writes only against data you intend to change.
7. Check the target app/server independently. Do not infer completion from model prose.
8. Add the file to `packages/`, bump its version when replacing a published
   definition, and regenerate the index as described in [repositories](repositories.md).

File reimports create separate instances. For testing updates rather than fresh
installs, use a stable raw HTTPS source or repository index.

Timeouts after submission mean `UNKNOWN`, not cancellation. Check the target
before retrying a write. An imported mutation following a tool result needs a
separate user request; “search then complete” should be two requests in this version.

## Org-agenda prerequisites

The example is not a generic adapter for every older org-agenda-api deployment.
It expects:

- `GET /agenda?span=&date=&include_overdue=`.
- `GET /get-all-todos?q=&limit=`, with `todos` and integer `total` describing
  matches before the server limit.
- `POST /capture` with `template` (default `default`) and `values.Title`.
- `POST /complete` with fixed `strict: true`, plus `id` or
  `file` + `pos` + exact `title`. A conflict must return HTTP 409 without a
  mutation; the package relies on that guarantee.
- `GET /custom-views` to list views and `GET /custom-view?key=` to run one.

Those server additions were implemented/tested but deployment and EVA HTTP device
verification were deferred. Configure the `org-agenda` basic-auth reference and
your HTTPS origin before using it. Its `mova://create?title=` example is a handoff
and requires mova to be signed in. `mova://capture` is a different, title-less
quick-capture dialog.

APIs without server search can use the local `items.filter` primitive shown in
[HTTP notes](examples/http-notes.json). That searches only returned data; it does
not fetch missing pages or provide strict write semantics to an older server.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| “Unexpected or missing fields” | Exact names and required fields in the [reference](package-format.md); unknown keys are rejected |
| Preview fails for a GitHub URL | Use `raw.githubusercontent.com`, not a `github.com/.../blob/...` page |
| Hash mismatch | Regenerate/publish the index, then refresh in EVA; hashes cover exact bytes |
| Changed package cannot install | Increase `version`; changed content at the same version and downgrades are refused |
| Plugin visible but model cannot use it | Enable/grant, reconnect, and check catalog overflow/availability |
| App not detected | Matching depends on Android visibility; try manual import and check actual intent handling |
| Activity unavailable | Install/enable the app, confirm exported activity and exact package/class for that version |
| Content or app-name action unavailable | These are parsed but not yet implemented by the Android host |
| HTTP credential missing | Match the reference name and approved origin; no paths or credentials in the origin |
| HTTP read is unknown | Check JSON shape/types, response limit, deadline, and HTTP 202 |
| HTTP write is unknown | Require real terminal evidence; a 2xx response alone is insufficient |
