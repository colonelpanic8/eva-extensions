# Mova package notes

The [Mova package](../packages/mova.json) targets Mova 7.0.1's Android
`mova://` interface and read-only content provider. Mova uses the active server
and credentials already configured in the app rather than exposing them through
this package.

EVA treats every successful Android activity launch as `HANDED_OFF`; it does not
consume Mova's activity result extras. The package therefore does not claim that
a todo mutation, refresh, search, or navigation completed. Mova must be logged in
for native todo operations. Provider reads return `COMPLETED` with bounded rows;
that receipt says nothing about a later intent action.

Each intent names Mova's intended exported activity as well as its package. Mova's
main activity also advertises broad `mova://` handling, so leaving the component
implicit can show an Android chooser between two activities in the same app.

## Consent and capture templates

`create_todo`, `complete_todo`, `update_todo`, and `reschedule_todo` pass the
literal query parameter `confirm=true`, so Mova shows its native confirmation
sheet even when its global headless-write setting is enabled. Mova always
confirms `delete_todo`. `refresh` never has a Mova confirmation sheet.

`create_todo` accepts a known template key and Mova's universal capture values:
`title`, `scheduled`, `deadline`, `priority`, `tags`, and `state`. It also passes
`body`, which only has an effect when the selected template declares a body
prompt. Mova can accept arbitrary query parameters whose names match prompts in
the selected template, but this repository package cannot expose them
generically: EVA v1 tool schemas are closed scalar objects and intent bindings
map only statically named arguments to statically named query parameters. A
custom package can add known prompt names explicitly, but the shared package
cannot discover a user's templates and change its tool schema at runtime.

## Discover templates and todos

Mova exposes a read-only provider at
`content://com.colonelpanic.mova.provider`. Its fixed `/templates` endpoint
returns `key`, `name`, `is_default`, `title_prompt`, `prompts_json`, and
`capture_uri`; `/todos`, `/todos/<id>`, and `/agenda` expose todo reads. Access
requires the dangerous Android permission
`com.colonelpanic.mova.permission.READ_TODOS`.

Package version 0.2.1 adds these reads beside the existing intent actions:

| Capability | Provider request | Next action |
| --- | --- | --- |
| `list_templates` | `/templates` | Pass `key` as `template` to capture or create |
| `find_todos` | `/todos?q=&limit=`; default limit 25, maximum 50 | Pick a todo and retain its location |
| `read_todo` | `/todos/{id}` with an encoded single-segment id | Inspect a discovered todo |
| `read_agenda` | `/agenda?date=&span=&include_overdue=&include_completed=` | Read day/week agenda rows |

Todo rows retain `id`, `file`, `pos`, and `title`. Some Org headings have no id;
for those, pass the returned `file`, `pos`, and `title` to `open_todo` or a
separately requested mutation. `read_todo` requires an id. `search_todos` and
`open_agenda` remain UI handoffs; they do not return provider rows. The intent
for opening a discovered id is `mova://open?id=`, not the provider URI.

Queries use typed URI slots, not SQL selection: Mova ignores the selection
parameter. Agenda `span` is the string `day` or `week`. EVA percent-encodes
values, so pass raw identifiers and search text. Reads have a 10-second deadline,
whole-row limits and a 14,000-byte row budget. EVA's `truncated` flag describes
its own row/byte cap; it does not incorporate Mova's cursor `total` extra or
prove that a server-limited search was exhaustive.

## Setup and verification

Use an EVA build containing content-provider execution (commit `000f95f` or
later). Earlier builds parse only fixed content URIs and cannot execute reads.
EVA declares Mova's provider authority for package visibility and its read
permission in the manifest. No AIDL service is needed.

After importing/updating and enabling the package, expand it in **Extensions**
and choose **Allow provider reads**. Android grants this dangerous permission on
each device; restoring EVA's configuration preserves the requirement but cannot
grant access. Open Mova and configure the active server first. Missing access
is a setup rejection; a provider failure or null cursor fails the read without
returning partial rows. A timeout after submission remains `UNKNOWN`.

The 0.2.1 contract requires re-enablement and renewed action grants. Its URI,
column and scalar mappings were checked against Mova 7.0.1's `TodoProvider`,
`ProviderRows`, and `TemplateProviderRows`, and decoded by EVA's JVM tests.
Device verification remains pending.
