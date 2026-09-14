# Mova package notes

The [Mova package](../packages/mova.json) targets Mova 7.0.1's Android
`mova://` interface. Mova uses the active server and credentials already
configured in the app rather than exposing them through this package.

EVA treats every successful Android activity launch as `HANDED_OFF`; it does not
consume Mova's activity result extras. The package therefore does not claim that
a todo mutation, refresh, search, or navigation completed. Mova must be logged in
for native todo operations.

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

## ContentProvider limitation

Mova exposes a read-only provider at
`content://com.colonelpanic.mova.provider`. Its fixed `/templates` endpoint
returns `key`, `name`, `is_default`, `title_prompt`, `prompts_json`, and
`capture_uri`; `/todos`, `/todos/<id>`, and `/agenda` expose todo reads. Access
requires the dangerous Android permission
`com.colonelpanic.mova.permission.READ_TODOS`.

The current EVA package codec can parse a fixed `android.content` URI,
projection, and SQL-style selection. The Android runtime cannot execute it:
`AndroidDeclarativeHost` reports every content binding unavailable and its query
method does not call `ContentResolver`. Packages also cannot add manifest
permissions, request dangerous permissions, or add provider-visibility entries.
Consequently this package deliberately has no template-list, todo-search, or
agenda-read capability.

Provider-backed template listing needs these EVA core changes:

1. Declare `com.colonelpanic.mova.permission.READ_TODOS` and a
   `<queries><provider android:authorities="com.colonelpanic.mova.provider"/></queries>`
   entry in EVA's Android manifest, then add an explicit runtime-permission flow
   for that dangerous permission.
2. Implement bounded, background-thread `ContentResolver.query` execution in
   `AndroidDeclarativeHost`, preserving the package projection, selection,
   maximum-row, and maximum-byte limits and returning attributed rows.

Those changes are sufficient for the fixed `/templates` endpoint. To expose
Mova's useful `/todos?q=&limit=`, `/todos/<id>`, and
`/agenda?date=&span=&include_overdue=&include_completed=` forms, EVA must also
extend the content binding with typed URI path/query slots. Its current content
URI is fixed and forbids a query string, while Mova's provider does not interpret
the binding's SQL-style `selection` as those endpoint parameters.
