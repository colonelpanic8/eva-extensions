# Repositories, imports, and updates

EVA fetches JSON over HTTPS; it does not clone Git repositories. GitHub is a
convenient host, but the configured URL must return a raw file with HTTP 200 and
without redirects.

## Layout and index

```text
README.md
index.json
packages/
  caffeine.json
  messages.json
  mova.json
update-index.py
docs/
```

Each package is self-contained. It cannot include another file, download code,
load a remote schema, or refer to a repository-local credentials file.

An index has exactly `formatVersion: 1` and `packages`. Each listing has exactly
the following fields (the digest below is illustrative):

```json
{
  "formatVersion": 1,
  "packages": [
    {
      "id": "community.example",
      "version": "0.1.0",
      "title": "Example",
      "url": "packages/example.json",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "androidPackages": []
    }
  ]
}
```

The index is limited to 1 MiB and 1,000 listings with unique IDs. A listing ID
is limited to 128 characters, version to 40, title to 120, and URL to 2,048.
`sha256` is exactly 64 lowercase hexadecimal characters over the exact package
file bytes, including whitespace and the final newline. `androidPackages` is
required in the index, even when empty, and must match the package array in order.

Relative URLs resolve against the index URL. Absolute URLs are allowed only on
the same HTTPS scheme, host, and port. Package files must match the listing's ID,
version, digest, and app hints. Unknown index keys are rejected. Use stable IDs
and source URLs.

Generate this repository's index with:

```sh
python3 update-index.py
git diff -- packages/ index.json
```

The generator reads direct `packages/*.json` files, sorts their names, checks for
duplicate IDs, and writes exact-byte hashes. It does not validate the complete
package format. Preview packages with EVA before release.

## Publish and refresh

For a new repository, add valid package files, generate the index, and publish
the packages and index together. Give users the raw index URL:

```text
https://raw.githubusercontent.com/OWNER/REPOSITORY/main/index.json
```

A normal GitHub repository URL or `blob/main/index.json` URL returns HTML or a
redirect and is not accepted. Download requests require HTTP 200, have a
20-second timeout, and refuse redirects, embedded URL credentials, and fragments.
Authenticated repositories are not supported.

In EVA, **Extensions → Browse → Refresh plugin repository** fetches listings.
Users select an entry, review the preview, then install or update it. Installation
uses the exact previewed bytes, without a second download. A mismatch after files
change means refresh and preview again.

## Versions and installed identity

The descriptive package ID is not an Android package ID, signature, or grant.
EVA creates an instance ID on first install. An update preserves that instance
only when the source and declared package ID match. Importing from a different
index or raw URL creates a separate installation even when the JSON has the same ID.

Changed canonical content must have a strictly higher three-part version.
Same-version changes and downgrades are refused. Bump for schema, binding,
description, title, receipt, version, or matching-hint changes; the whole
canonical document participates in grants. Formatting and object-key order change
the index byte hash but do not change the canonical contract digest. Array order does.

An unchanged contract retains grants. A changed contract requires re-enablement
and write grants again; a larger version does not confer trust. Replacement is
validated before it overwrites the working installation. Historical receipts
retain prior attribution. Removing a plugin removes its installed definition;
it does not uninstall the target app or undo external actions.

A standalone raw HTTPS package URL supports the same preview and install flow
without an index. File imports are bounded and receive a fresh source and instance
identity. Reimporting a local file is not an update.

Current storage limits are 64 imported instances and 4 MiB total serialized
installation storage. Model connections admit at most 64 tools: controls first,
then bundled tools, then extensions by qualified ID. Overflow is unavailable with
an explanation.

## App matching and icons

Put exact Android application package IDs in `androidPackages`. EVA matches them
locally and uses icons supplied by installed apps. Hints do not constrain binding
destinations, authenticate the publisher, install a plugin, or grant execution.

Android package visibility can hide an installed app. “Not detected” does not
prove incompatibility; manual imports remain available. Server-only or generic
handler plugins should use an empty hint array. Never collect or upload the user's
app inventory as part of repository matching.

## Maintenance checklist

- Use an existing documented interface and accurate effect/result descriptions.
- Keep secrets out; refer to credentials by name.
- Check the [supported binding status](authoring.md#choose-an-interface).
- Validate full JSON in EVA's preview, then test a safe real invocation.
- Bump the version and regenerate exact-byte hashes together.
- Check all local Markdown links and label hypothetical examples explicitly.
- Record device verification separately from codec/JVM verification.
