# HTTP notes example

[http-notes.json](http-notes.json) is a complete, parser-valid package for a
**hypothetical** API. It is outside the repository index and does not point to a
working server. Replace the origin and configure the named `notes` basic-auth
reference to use an API with this contract.

A GET /notes response:

```json
{
  "notes": [
    {"id":"note-1","title":"Buy milk","category":"errands"},
    {"id":"note-2","title":"Read a book","category":"home"}
  ],
  "total": 2
}
```

With argument `q: "milk"`, EVA renders:

```text
id="note-1" title="Buy milk" category="errands"
```

The query is used locally, not sent as an HTTP parameter. A greater total than
returned array size causes a source-truncation warning, even if the local filter
found no match. Optional missing category renders null.

POST /notes sends a JSON object such as
`{"title":"Buy milk","source":"eva"}`. Terminal response:

```json
{
  "status": "created",
  "note": {"id":"note-3","title":"Buy milk"}
}
```

The exact `/status == "created"` evidence permits COMPLETED and `/note` is
rendered as JSON. HTTP 202, missing evidence, invalid JSON, or lost replies do
not prove completion and produce UNKNOWN. The sample intentionally declares no
pre-execution rejection status: that requires a real API guarantee.
