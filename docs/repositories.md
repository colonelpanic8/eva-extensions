# Repositories, imports, and updates

A package catalog is a Git repository with one self-contained JSON file per
package under `packages/`. Nothing else is required: no index, no digests, no
build step.

```text
README.md
packages/
  caffeine.json
  google-maps.json
  messages.json
  mova.json
docs/
```

EVA keeps a read-only clone of the configured catalog on the phone. Opening
**Extensions → Browse** lists the commit pinned in the configuration. **Update**
(or **Update all**) fetches the current branch, installs or updates matching
extensions according to their auto-enable choices, and records the new commit.
A file that does not decode is named and skipped; duplicate declared IDs fail
the listing. Previews read the exact listed commit even if a later update moves
the checkout.

Portable configuration version 4 stores references instead of copying catalog
JSON into the user's repository:

```yaml
packages:
  repositories:
  - https://github.com/colonelpanic8/eva-extensions.git
  revisions:
    https://github.com/colonelpanic8/eva-extensions.git: <full 40-character commit SHA>
  installed:
  - instance: <stable installation ID>
    source: https://github.com/colonelpanic8/eva-extensions.git
    url: packages/clock.json
    id: android.clock
```

Use the package's declared `id` and retain existing instance IDs during migration.
A package can override the shared pin with its own `revision`, for example when
its update failed and the previous working version was retained. Restore fetches
and validates the exact commit before applying configuration; it never silently
substitutes the latest version. Installed definitions and fetched Git objects
remain cached for offline use. Fresh restores need network access unless EVA
ships that exact default definition. File and raw-URL imports retain inline
`document` content because they have no immutable Git reference.

The catalog remote must be an HTTPS Git URL without credentials, for example:

```text
https://github.com/colonelpanic8/eva-extensions.git
```

The clone tracks the branch that was the remote's default when it was first
cloned. Private catalogs are not supported.

A package can also be previewed from a raw HTTPS URL of the file itself, or
imported from a local file through **Import extension file**. Each file import gets
its own source and instance identity; reimporting a file is not an update.

## Versions and installed identity

The descriptive package ID is not an Android package ID, signature, or grant.
EVA creates an instance ID on first install and preserves it while the source
repository and declared package ID match. The same JSON installed from a
different catalog or a raw URL is a separate installation.

Changed canonical content must have a strictly higher three-part version.
Same-version changes and downgrades are refused. Bump for schema, binding,
description, title, receipt, version, or matching-hint changes; the whole
canonical document participates in grants. Formatting and object-key order do
not change the canonical contract digest. Array order does.

An unchanged contract retains grants. A changed contract invalidates old grants;
the configured auto-enable policy determines whether EVA enables the new contract.
An explicit disable is preserved across updates. Replacement is
validated before it overwrites the working installation. Historical receipts
retain prior attribution. Removing an extension removes its installed definition;
it does not uninstall the target app or undo external actions.

Current storage limits are 64 imported instances and 4 MiB total serialized
installation storage. Model connections admit at most 64 tools: controls first,
then bundled tools, then extensions by qualified ID. Overflow is unavailable with
an explanation.

## App matching and icons

Put exact Android application package IDs in `androidPackages`. EVA matches them
locally and uses icons supplied by installed apps. Hints do not constrain binding
destinations, authenticate the publisher, install an extension, or grant execution.

Android package visibility can hide an installed app. “Not detected” does not
prove incompatibility; manual imports remain available. Server-only or generic
handler extensions should use an empty hint array. Never collect or upload the user's
app inventory as part of repository matching.

## Maintenance checklist

- Use an existing documented interface and accurate effect/result descriptions.
- Keep secrets out; refer to credentials by name.
- Check the [supported binding status](authoring.md#choose-an-interface).
- Validate full JSON in EVA's preview, then test a safe real invocation.
- Bump the version with every content change and commit the package file.
- Check all local Markdown links and label hypothetical examples explicitly.
- Record device verification separately from codec/JVM verification.
