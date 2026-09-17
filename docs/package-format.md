# Declarative package format v1

This is the author-facing contract for JSON plugins. It describes EVA's parser
and Android host including content execution at commit `000f95f`. Start with the
complete example in [authoring](authoring.md). EVA also
publishes a JSON Schema for this format at
[`docs/schemas/package.schema.json`](https://github.com/colonelpanic8/eva/blob/main/docs/schemas/package.schema.json);
the Kotlin codec remains the oracle where they disagree.

## Document and capability envelope

All objects reject unknown fields. JSON must have valid Unicode and no duplicate
keys. There are no comments, scripts, expressions, or arbitrary schema extensions.
The full UTF-8 document is at most **262,144 bytes (256 KiB)**, with JSON nesting
bounded to 16 levels.

| Root field | Required | Meaning |
| --- | --- | --- |
| `formatVersion` | Yes | Integer `1` |
| `id` | Yes | Lowercase dotted ID, at most 128 characters; e.g. `community.notes`. Each segment starts with a lowercase letter and continues with lowercase letters, digits, `_`, or `-`; at least two segments |
| `version` | Yes | Three numeric components `MAJOR.MINOR.PATCH`; each 0–999999999, no leading zeros except 0, no suffixes |
| `title` | Yes | Nonempty display title, at most 120 characters |
| `androidPackages` | No | Up to 16 distinct Android package IDs, each at most 200 characters and using the same dotted syntax; defaults to `[]`. Matching hints only |
| `capabilities` | Yes | 1–64 capability objects, with unique tool names |

A capability has these fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `tool` | Yes | An MCP tool object: `name`, `title`, `description`, `inputSchema`, and optional `outputSchema`, `annotations`, `_meta` |
| `effects` | No | `read`, `write`, `external_handoff`, or `unknown`; defaults to unknown |
| `execution` | Yes | Execution contract below |
| `binding` | Yes | One binding below |
| `validators` | No | Map from string argument names to supported named validators |
| `receipts` | No | `success` and/or `handlerMissing`, each 1–1,000 characters |
| `_meta` | No | Any object. EVA digests it into the contract but never interprets it; the only place for vendor data |

Tool names match `[A-Za-z_][A-Za-z0-9_]{0,63}`; titles are 1–120 characters and
descriptions are 1–2,000. Tool names are local to the plugin; EVA assigns qualified capability
IDs from the installed instance. Do not hard-code EVA's instance ID in a package.
Titles, descriptions, and receipt text are attributed external data. They cannot
override grants, status, or model policy.

`tool.annotations` may carry MCP's `title`, `readOnlyHint`, `destructiveHint`,
`idempotentHint`, and `openWorldHint`. They are hints for models and other MCP
clients; `effects` remains EVA's authority, and a `readOnlyHint` or
`destructiveHint` that contradicts the effective effect is rejected.
`tool.outputSchema` is optional and describes the structured `data` a result
carries (see [result projection](#result-projection)); its root is an object and
it may nest objects and arrays, unlike the input schema.

Optional `description` (up to 2,000 characters) says what the extension is for,
and optional `setup` is 1–8 short strings (up to 300 characters each) naming what
the user must do outside EVA before the actions work. EVA shows both above the
capability list when the user reviews an install, and both are part of the
canonical document, so changing them changes the digest and requires
re-enablement. State requirements, not assurances: an extension cannot vouch for
its own trustworthiness or verification.

## Input schema

The root schema is a closed object. Required keys, even for no-argument tools:

```json
{"type":"object","properties":{},"required":[],"additionalProperties":false}
```

An optional root `description` is allowed. Up to 64 properties may be declared;
property names match `[A-Za-z][A-Za-z0-9_]{0,63}` (unlike tool names, no initial
underscore). `required` lists distinct declared names.

| Property type | Allowed keys in addition to `type` |
| --- | --- |
| `string` | `description`, `enum`, `minLength`, `maxLength` |
| `integer`, `number` | `description`, `enum`, `minimum`, `maximum` |
| `boolean` | `description`, `enum` |
| `array` | `description`, `items` (one scalar schema from the rows above), `minItems`, `maxItems` (0–64) |

Descriptions are 1–2,000 characters. Enums contain 1–64 distinct values of the
declared type satisfying its bounds. String length limits are integers 0–65,536
and count Unicode code points. Numeric limits are inclusive and finite; integer
values/bounds must be within ±9,007,199,254,740,991. Minimum must not exceed maximum.
Use explicit bounds suitable for the destination, especially on strings.

Inputs cannot be nested objects, arrays of objects, null, or type unions. No `default`,
`pattern`, `format`, `$ref`, `oneOf`, `anyOf`, `allOf`, or arbitrary
keywords. A subset of MCP tool JSON is compatible; this does not make EVA an MCP
server or allow importing every MCP schema.

Named validators apply to string inputs: `phoneNumber` (one phone number in
EVA's accepted syntax: optional +, one digit, then 2–24 digits/spaces/parentheses/hyphens), `httpUrl` (absolute HTTP(S), host, valid port, no user
info), and `emailAddress` (one address, 3–320 characters, one non-edge @, no
whitespace/control characters or `,;<>`). These are syntax checks, not delivery
or account verification. Missing optional inputs are skipped. Unknown validator
names are rejected. Defaults should also satisfy the intended validator.

A property may also be a string map: `{"type":"object","maxProperties":16,
"additionalProperties":{"type":"string","maxLength":2000}}` with no `properties` or
`required`. The request chooses the keys (1–64 characters each, at most
`maxProperties` of them); the package bounds only the value shape. Use it when the
target defines parameter names at runtime, such as Mova capture prompts, and pair
it with an intent `querySpread`.

## Typed slots and conditional selection

Slots are used for query values, extras, HTTP parameters/body leaves, and content
path/selection values. Two forms:

```json
{"argument":"title","type":"string","default":"Untitled","required":true}
```

```json
{"value":true,"type":"boolean"}
```

`type` is string/integer/number/boolean. An argument slot must refer to a tool
property of the exact same type. Optional `default` is a non-null scalar meeting
that property's schema; optional `required` is a boolean, default false. A string
argument slot whose property declares an `enum` may add `values`, an object mapping
every enum value to the string actually sent, e.g.
`{"argument":"travelmode","type":"string","values":{"driving":"d","bicycling":"b"}}`;
the keys must equal the enum exactly and each value is 1–200 characters.
Literal slots have exactly `value` and `type`, with a matching non-null scalar.
Inside an HTTP `requestBody` only, an argument slot may use `type: "array"` to
place a whole scalar-list argument as a JSON array (with an optional array
`default`); query, path, extras, opaque, and selection slots stay scalar.

Tool-schema required inputs are validated **before** binding defaults. To use a
default when the user omits input, leave it out of the schema's `required`.
Defaults apply only at that slot; they do not populate other slots, filters, or
conditional selection. An absent optional query, extra, or body leaf is omitted.
Path, opaque URI, and content selection slots must resolve to a value.

A `select` binding has exactly `kind: "select"`, `argument`, `present`, and
`absent`. It picks a fully declared branch based on presence of the named tool
argument, not its truthiness or a default. Nested selects are rejected. Both
branches must agree with the capability's execution mode; effects account for
both.

## Execution, effects, grants

The `execution` contract:

```json
{
  "mode": "synchronous",
  "requiresForeground": false,
  "maxWaitMillis": 30000
}
```

`mode` (`synchronous` or `handoff`) and `requiresForeground` are required.
`maxWaitMillis` is optional, null or a positive integer. There are no other
execution fields. Intents require
handoff and foreground true; HTTP/content require synchronous mode. Set
foreground according to whether the operation needs EVA's visible activity.

Effective wait: user per-instance override, else capability `maxWaitMillis`,
else EVA's mode default (20 seconds voice, 30 seconds typed; globally adjustable).
A hard 60-second ceiling applies to every layer. Receipts include the layers and
chosen budget. Voice displays a waiting cue halfway through. Expiry after
submission reports `UNKNOWN`; it does not prove the target stopped.

EVA limits execution to four global calls and one per extension instance, refusing
busy calls instead of queuing. There are no accepted-job/polling/callback contracts
in v1, no automatic retry of uncertain work, and interruption is not undo.

Effect floors: content queries are at least read; intents are at least external
handoff; POST/PUT/PATCH/DELETE are writes. Omitted/unknown effects remain unknown.
GET is not automatically read:
declare read only when accurate. All non-read effects need individual grants.
The user enables a plugin to grant claimed reads. No file field grants authority
automatically. Imported mutations after a tool result need a new user request.
Additions become model-visible on reconnect; revocation blocks new execution.

## Android intent binding

Required: `kind: "android.intent"`, `action`.
Optional: `uri`, `extras`, `package`, `class`, `mimeType`, `packageByName`.

- `action`: fixed string up to 200 characters, starting with a letter and
  otherwise letters, digits, underscores, or dots. Or a string argument slot with a
  `values` map covering the argument's enum, every value being such an action:
  `{"argument":"screen","type":"string","required":true,"values":{"wifi":"android.settings.WIFI_SETTINGS"}}`.
  The publisher still lists every action that can launch.
- `package`: fixed dotted package ID. `class` requires package and a fully
  qualified fixed activity name, up to 300 characters. Android export and
  permission checks still apply. No model-supplied class, flags, or component.
- `uri`: `{base, query?, path?}`, `{base, opaque}`, or `{argument, schemes}`. Base is
  fixed, absolute, up to 2,000 characters, with no query, fragment, or user info.
  Schemes `intent`, `file`, `javascript`, and `data` are forbidden; a `content:`
  base is accepted only with no query, path, or opaque slot at all, for a fixed
  provider insert such as `content://com.android.calendar/events`.
  `{"argument":"url","schemes":["http","https"]}` launches the named string
  argument as the whole data URI when it parses as absolute with a listed scheme;
  pair it with the `httpUrl` validator. Use this only for a tool whose purpose is
  opening an address the user chose, as in [Web](../packages/web.json).
- `path`: maps `{name}` placeholders written into the base after its scheme to
  slots, as in `google.navigation:q={destination}&mode={mode}`. Each value is
  percent-encoded whole and must be present and nonempty at invocation. Every
  placeholder needs one mapping and vice versa; a placeholder cannot form the
  scheme. See [Google Maps](../packages/google-maps.json).
- `querySpread`: `{"argument":"prompts"}`, naming a string-map argument whose entries
  are appended as further percent-encoded query parameters after the fixed ones. An
  entry whose key equals a fixed query name in any letter case is refused; the
  request can add parameters but never replace a fixed one. Needs a fixed base
  and no `opaque` slot. See [Mova](../packages/mova.json) `create_todo`.
- `query` and `extras`: maps of fixed names to slots, at most 64 each.
  Names are 1–200 characters, without control characters. Missing optional values
  are omitted. Query names/values are percent-encoded; never pre-encode arguments.
- `opaque`: string slot, with scheme-only base such as `smsto:` or `tel:`.
  The entire value is encoded and appended. Cannot coexist with query or path;
  equivalent to `base: "smsto:{number}"` with one path slot.
- `mimeType`: fixed lowercase MIME type, e.g. `text/plain`; not a slot.
- `packageByName`: name of a string input; mutually exclusive with package.
  **Parsed but Android execution currently refuses it.** Do not publish an action
  relying on this field as usable yet.

Extras use Android String, Boolean, Int for integral values fitting 32 bits,
Long for larger integral values, and Double otherwise. No parcelables or arrays.

A launch returns `HANDED_OFF`. A missing handler/component returns
`NOT_EXECUTED`; fixed-component failures include install/enable/update guidance
and take precedence over custom handler-missing copy. `receipts.success` changes
handoff display text only. Missing targets do not themselves rewrite the catalog.

## HTTP binding

Required: `kind: "http"`, `origin`, `method`, `path`, `parameters`,
`maxResponseBytes`, `result`. Optional: `requestBody`, `credential`.

| Field | Contract |
| --- | --- |
| `origin` | Fixed HTTPS scheme/host, optional port; no trailing slash, path, user info, query, or fragment |
| `method` | GET, HEAD, POST, PUT, PATCH, DELETE (uppercase) |
| `path` | Starts with a single /; no query, fragment, backslash, percent escapes, whitespace/control characters, or . / .. segments |
| `parameters` | Up to 64 `{in,name,value}` objects. `in` is path/query; `value` is a slot; name is an ASCII identifier |
| `requestBody` | Object mapping `{"fields":{...}}`; leaves are slots (scalar or array argument slots) and child objects are further fields mappings; up to 64 fields per object |
| `credential` | Named basic-auth reference matching `[a-z][a-z0-9_-]{0,63}`; no secret in the document |
| `maxResponseBytes` | Integer 1–1,048,576; oversized responses are rejected, not partially parsed |
| `result` | Result mapping below |

Path placeholders such as `/notes/{id}` must exactly match path parameter names.
Values are encoded; empty, "." and ".." path values are refused. There are no
header slots, raw body templates, or GET/HEAD bodies; the only arrays a body can
carry are whole array-typed tool arguments.
Body field names are ASCII identifiers. URL and encoded body are each bounded to
16 KiB; incoming tool arguments are also bounded to 16 KiB.

Basic auth is resolved by reference name in EVA's extension secret store, scoped
to the approved origin (not model credentials). Configure URL/username/password
in **Extensions → Settings**. User origin configuration is applied before
approval/digesting, not supplied by model arguments. Runtime refuses a request
outside that origin. Redirects and automatic retries/follow-ups are disabled,
including same-origin redirects. The API must return JSON directly at the URL.
There is no Bearer/OAuth/custom-header credential format in v1.

### Result projection

Required `maxBytes` is 1–16,384. Choose **exactly one** of:

- `pointer`: JSON Pointer selecting a string (rendered as text) or any JSON
  value (rendered as JSON). Empty pointer selects the entire response.
- `items`: bounded one-line-per-item projection described below.

Optional `evidence: {pointer, equals}` compares a root-relative response field
to an exact non-null scalar. Use it for a **pointer-based write** whose API
documents terminal success. Item-based writes currently always report unknown,
even if evidence is supplied. Choose pointer projection for confirmed writes.

Optional `notExecutedStatuses` is an array of HTTP 400–499 codes. Declare only
codes the API guarantees mean **no mutation occurred**. It produces
`NOT_EXECUTED` without projecting the response body. Never add generic errors
here just to hide uncertainty.

Pointers are empty or start with /, at most 1,000 characters. Escape ~ as ~0 and /
as ~1. Ordinary pointers support object keys and zero-based array indices;
they have no wildcard or JSONPath expressions.

| Response | Outcome |
| --- | --- |
| Explicit `notExecutedStatuses` | `NOT_EXECUTED` |
| HTTP 202 | `UNKNOWN`; no polling is inferred |
| Other non-2xx | `FAILED` for declared reads, otherwise `UNKNOWN` |
| 2xx read with valid projection | `COMPLETED` |
| 2xx pointer write with matching evidence and existing result field | `COMPLETED` |
| 2xx write without that evidence | `UNKNOWN` |
| Missing pointer result field | `FAILED` for read, otherwise `UNKNOWN` |
| Invalid JSON/types, oversized response, transport failure after submission, timeout | Conservatively `UNKNOWN` |

Empty bodies (including normal HEAD/204 responses) are not valid JSON results.
Even reads should use endpoints with a JSON body. A successful HTTP status alone
does not establish write completion. Projected text is untrusted and attributed.
Byte truncation of pointer text preserves UTF-8 and appends an EVA-owned note;
the note/receipt envelope may exceed the projection's byte budget.

Results also carry structured `data` beside the text, which EVA journals with the
receipt and hands to the model as quoted external data. A `pointer` result whose
selected value is a JSON object becomes the data as-is. An `items` result becomes
`{"items": [...], "truncated": bool, "sourceTruncated": bool, "total": n?}` where
each item is an object keyed by slot name with the typed values (string, number,
boolean, string array, or null); exactly the items that appear as whole lines in
the text appear in the data. Content queries attach `{"rows": [...], "truncated":
bool}`. Data larger than 16 KiB is omitted whole rather than cut. Declare
`tool.outputSchema` when you want that shape documented for models and clients.

### Item mapping and local filter

See the complete [HTTP notes example](examples/http-notes.json).

| `items` field | Required | Contract |
| --- | --- | --- |
| `arrayPaths` | Yes | 1–4 paths, first available location wins. Paths traverse object keys; one * segment may enumerate object values or array elements to reach arrays |
| `line` | Yes | Fixed 1–2,000 character line template with `{fieldName}` slots, no control characters |
| `fields` | Yes | 1–32 named slots, each `{pointer,type,required?}`; all slots must occur in line, no undeclared slots |
| `maxItems` | Yes | 1–100 |
| `truncationNote` | Yes | 1–500 characters, no control characters; appended when capped |
| `totalPointer` | No | Root pointer to nonnegative total source count before local filtering; missing/null means unavailable |
| `filter` | No | `{fields: ["/title", "/category"], argument: "q"}` |

Item field pointers resolve relative to each item. Types are string, integer,
number, boolean, or `stringArray`. Required defaults false. Missing/null optional
fields render `null`; required missing fields and wrong types invalidate the
projection. Strings/arrays are JSON-quoted, preserving exact identifiers and
keeping newlines inside one output line. Items must be objects.

Array-path traversal is bounded to 4,096 nodes per step; this is not general
JSONPath. A present but wrongly typed array location fails instead of silently
guessing another shape. "/days/*" can select grouped arrays. Ordinary field and
total pointers do not support *.

Filter fields are 1–16 distinct item-relative pointers; argument names a string
tool input. Keep an item if any pointed-to **string** contains the argument,
case-insensitively. Null, absent, numeric, array, and object fields do not match.
Missing optional query disables filtering; an empty query matches any present
string. Binding defaults do not supply filter queries.

Filter before the item cap, preserve source order, then emit whole lines within
the byte budget. Never emit partial identifiers. More matching items than the cap
or exhausted line space causes a truncation note. If total exceeds the returned
source count, flag source truncation even if the filter found no matches.
Without total/completeness metadata, no claim is made about data not returned.
There is no sorting, ranking, joins, calculations, regex, scripting, pagination,
network follow-up, conditional line formatting, or recursive array search.

## Content binding

Required: `kind: "android.content"`, `authority`, `uri`, `projection`,
`maxRows`, `maxBytes`. Optional: `selection`.

Authority is a fixed dotted ID, up to 200 characters. URI accepts a legacy fixed
`content://` string or `{base, query?, path?}`. Base uses that exact authority,
with no query/fragment, user info or port, up to 2,000 characters. Object bases
also reject percent escapes, whitespace, backslashes and dot segments. Arguments
can never choose an authority, column or SQL fragment.

```json
{
  "base": "content://com.colonelpanic.mova.provider/todos/{id}",
  "path": {"id": {"argument": "id", "type": "string"}}
}
```

Query maps at most 64 fixed names (1–200 characters, no controls) to scalar
slots. Names and values are percent-encoded; an absent optional argument is
omitted unless its slot has a default. Path maps at most 64 identifier names
to scalar slots matching every `{name}` placeholder exactly. Each path slot must
resolve; empty, `.`/`..`, slash and backslash values are rejected. Pass raw
values, never pre-encoded strings. The expanded URI is bounded to 16 KiB.

Projection maps 1–32 identifier column names to scalar types, or to `json` for a
text cell that EVA decodes into structured data (within the result budget) so an
embedded document such as Mova's `prompts_json` reaches the model as data.
Selection cannot target a `json` column.
Selection is up to 16 `{column,operator,value}` predicates joined with AND;
columns must be projected, slots must match the column type, and operators are
=, !=, <, <=, >, >=, LIKE (LIKE only for strings). Values become bound selection
arguments, not SQL fragments. `maxRows` is 1–100; `maxBytes` is 1–16,384.

EVA issues `ContentResolver.query` on bounded background workers with a
`CancellationSignal`, exactly the declared projection, bound selection arguments,
and no sorting. Mova and Paseo use URI parameters for filtering; do not add SQL
selection to those packages. There is no free-form SQL or insert/update/delete.

Results contain attributed JSON text and structured `data: {"rows": [...],
"truncated": bool}` with the same whole rows. Strings require string cursor
cells, integers integer cells in the exact-integer range, numbers finite numeric
cells, and booleans integer 0/1; null remains null. Blobs and implicit coercion
fail the read. `maxBytes` bounds the UTF-8 JSON row array including escaping and
separators; EVA reserves room for the structured object's 16 KiB limit. Empty
array and EVA-owned annotations are envelope overhead. No ID is cut in half.

The host reads at most `maxRows` rows plus a lookahead and flags its row/byte
truncation. It cannot infer rows omitted by a provider-side limit or cache.
Describe those limits in tools. A completed read returns `COMPLETED`;
missing/invisible providers or permissions return `NOT_EXECUTED` with setup
guidance, and provider `SecurityException` returns `NOT_EXECUTED` with caller
authorization guidance. Unknown columns, invalid cell types, null cursors and
other query failures return `FAILED` without partial data. A deadline before
submission returns `NOT_EXECUTED`; after submission it returns `UNKNOWN` and
requests cancellation. Reads are never retried. The deadline includes provider
acquisition and cursor traversal; late cursors are closed.

### Visibility and permission setup

EVA's manifest declares `com.colonelpanic.mova.provider` and `sh.paseo.assistant`
in `<queries><provider android:authorities="..."/></queries>`. Per-authority
entries let existing apps expose providers without an AIDL service or a new
advertisement component. Provider metadata alone cannot make a package visible.
No `QUERY_ALL_PACKAGES` is used. Other providers need an existing visibility
route or an EVA manifest update; importing JSON cannot add one.

EVA also declares Mova's dangerous
`com.colonelpanic.mova.permission.READ_TODOS` permission. **Extensions → expand
the package → Allow provider reads** launches Android's runtime request. Paseo
uses no dangerous permission and enforces its own caller policy. All queries
recheck Android access; enabling the package does not bypass either app's checks.
Additional custom dangerous permissions require an EVA manifest/allowlist change;
there is no model-supplied permission slot.

Installed package bytes, enablement and action grants use EVA's portable
configuration. Supported content permissions participate in `device.authorizations`
in `eva.yaml`; restoring it reports missing providers/permissions and requires
device-local authorization. Configuration cannot grant Android permission.
See [Mova setup](mova.md#setup-and-verification) and [Paseo's catalog](paseo.md#where-the-ids-come-from).
