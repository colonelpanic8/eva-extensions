# Repositories, imports, and updates

EVA fetches JSON over HTTPS; it does not clone git repositories. GitHub is a
convenient host, but any HTTPS host returning raw files without redirects works.

## Layout and index

```text
README.md
index.json
packages/
  caffeine.json
  messages.json
  org-agenda.json
update-index.py
docs/
```

Each package is self-contained. It cannot include another file, download code,
load a remote schema, or refer to a repository-local credentials file.

An index has exactly `formatVersion: 1` and `packages`. Each listing has exactly
the following fields (the digest below is illustrative, not usable):

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

Index limit: 1 MiB and 1,000 listings, with unique IDs.
Listing bounds: ID 128 characters, version 40, title 120, URL 2,048.
SHA-256 is exactly 64 lowercase hexadecimal characters over **exact package
file bytes**, including whitespace and final newline. `androidPackages` is
required in the index, even when empty, and must match the package array in order.

Relative URLs resolve against the index URL. Absolute URLs are allowed only on
the same HTTPS scheme, host, and port. Package files must match the listing's ID,
version, digest, and app hints. Keep the listing title aligned too. Unknown index
keys are rejected. Use stable IDs and stable source URLs.

Generate this repository's index with:

```sh
python3 update-index.py
git diff -- packages/ index.json
```

The generator reads `packages/*.json`, sorts filenames, checks duplicate IDs,
and writes hashes. It does not validate the complete package format. Preview the
file with EVA before release.

## Publish and refresh

For a new repository, copy the layout, add valid package files, generate the
index, and publish both files and index together. Give users the raw index URL:

```text
https://raw.githubusercontent.com/OWNER/REPOSITORY/main/index.json
```

A normal GitHub repository URL or `blob/main/index.json` URL returns HTML and is
not accepted. Download requests require HTTP 200, have a 20-second timeout, and
refuse redirects, embedded URL credentials, and fragments. Authenticated/private
repository browsing is not supported by this fetcher.

In EVA, **Extensions → Browse → Refresh plugin repository** fetches listings
only. Users select an entry, review the preview, then install/update. Installation
uses the exact previewed bytes, not a second download. A mismatch after files
change means refresh and preview again.

## Versions and installed identity

The descriptive package ID is not an Android package ID, signature, or grant.
EVA creates an instance ID on first install. An update preserves that instance
only when the source and declared package ID match. Importing from a different
index/raw URL creates a separate installation even if the JSON has the same ID.

Changed canonical content must have a strictly higher three-part version.
Same-version changes and downgrades are refused. Bump for schema, binding,
description, title, receipt, version, or matching-hint changes; the **whole
canonical document** participates in grants. Changing only formatting/object
key order changes the index's byte hash but not the canonical contract digest.
Changing array order does change the digest.

An unchanged contract retains grants. A changed contract requires re-enablement
and write grants again; a larger version does not confer trust. Replacement is
validated before it overwrites the working installation. Historical receipts
retain prior attribution. Removing a plugin removes its installed definition;
it does not uninstall the target app or undo external actions.

A standalone raw HTTPS package URL supports the same preview/install process
without an index. For file-picker imports EVA copies bounded bytes and creates a
fresh source/instance on each import. Reimporting a local file is not an update.
Use HTTPS when you want a stable update channel.

Current storage limits are 64 imported instances and 4 MiB total serialized
installation storage. Model connections admit at most 64 tools: controls first,
then bundled tools, then extensions by qualified ID. Overflow is unavailable
with an explanation, not silently executed.

## App matching and icons

Put exact Android application package IDs in `androidPackages`. EVA matches
locally and uses icons supplied by installed apps. Hints do not constrain the
binding's destinations, authenticate the publisher, install a plugin, or grant
execution. A fixed intent package/class is a separate binding constraint.

Android package visibility can hide an installed app. “Not detected” does not
prove incompatibility; manual imports remain available. Server-only or generic
handler plugins should use an empty hint array. Never collect or upload the
user's app inventory as part of repository matching.

## Maintenance checklist

- Use an existing documented interface and accurate effect/result descriptions.
- Keep secrets out; refer to credentials by name.
- Check the [supported binding status](authoring.md#choose-an-interface).
- Validate full JSON in EVA's preview, then test a safe real invocation.
- Bump the version and regenerate exact-byte hashes together.
- Check all local Markdown links and label hypothetical examples explicitly.
- Record device verification separately from codec/JVM verification.
