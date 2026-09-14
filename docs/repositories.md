# Git repositories, imports, and updates

EVA shallow-clones plugin repositories over HTTPS into app-private storage.
GitHub is a convenient host, but any publicly readable HTTPS Git remote works.

## Layout

```text
README.md
packages/
  caffeine.json
  messages.json
  mova.json
  org-agenda.json
docs/
```

Each package is self-contained. It cannot include another file, download code,
load a remote schema, or refer to a repository-local credentials file.

EVA reads direct `packages/*.json` children, sorted by filename, with at most
1,000 packages and unique package IDs. Each file is decoded with the normal
bounded package codec. Subdirectories and symbolic links are not package entries.
All listing metadata comes from the package itself. Use stable IDs and a stable
repository URL.

## Publish and refresh

For a new repository, copy the layout, add valid package files, and publish the
Git repository. Give users its HTTPS clone URL:

```text
https://github.com/OWNER/REPOSITORY.git
```

Repository URLs must use HTTPS, end in `.git`, and contain no embedded credentials
or fragments. Authenticated/private repository browsing is not supported.

In EVA, **Extensions → Browse → Refresh plugin repository** replaces the local
shallow checkout and rebuilds its listings. Users select an entry, review the
preview, then install/update. Installation uses the exact bytes captured during
refresh, not a second read or download.

## Versions and installed identity

The descriptive package ID is not an Android package ID, signature, or grant.
EVA creates an instance ID on first install. An update preserves that instance
only when the source and declared package ID match. Importing from a different
repository/raw URL creates a separate installation even if the JSON has the same ID.

Changed canonical content must have a strictly higher three-part version.
Same-version changes and downgrades are refused. Bump for schema, binding,
description, title, receipt, version, or matching-hint changes; the **whole
canonical document** participates in grants. Changing only formatting/object
key order does not change the canonical contract digest. Changing array order does.

An unchanged contract retains grants. A changed contract requires re-enablement
and write grants again; a larger version does not confer trust. Replacement is
validated before it overwrites the working installation. Historical receipts
retain prior attribution. Removing a plugin removes its installed definition;
it does not uninstall the target app or undo external actions.

A standalone raw HTTPS package URL supports the same preview/install process
without a Git repository. For file-picker imports EVA copies bounded bytes and creates a
fresh source/instance on each import. Reimporting a local file is not an update.
Use a Git repository when you want a stable update channel.

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
- Bump the version whenever canonical package content changes.
- Check all local Markdown links and label hypothetical examples explicitly.
- Record device verification separately from codec/JVM verification.
