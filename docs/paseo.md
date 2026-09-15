# Paseo package notes

The [Paseo package](../packages/paseo.json) drives the Android app's
`paseo://` links, documented in Paseo's `docs/android-intents.md`. Every
capability is an `ACTION_VIEW` launch of a fixed `paseo://` base with query
slots, so any Paseo build that registers the scheme handles it; the package pins
no application package because Paseo ships under more than one id
(`sh.paseo` from the stores, `sh.paseo.assembly` for a personal build) and a
binding can pin only one. `androidPackages` lists both as matching hints.

EVA treats every successful launch as `HANDED_OFF`. Paseo resolves the host,
agent, and workspace itself and shows its own toast when an ID is unknown; EVA
does not receive that. Paseo hosts are named by `serverId`; when omitted, Paseo
uses the host of the last opened workspace, then the only configured host, and
otherwise refuses with a toast asking for one.

## Drafts versus sends

`new_agent` and `draft_agent_prompt` only place text in a composer. The user
picks the project (for a new agent) and taps Send in Paseo. `send_agent_prompt`
adds the literal `send=true` and is declared a write: Paseo sends the prompt
without a tap only when the user has turned on **Settings → General → Send
prompts from links**, because any app can open a `paseo://` link and an agent
runs commands on the host. With the setting off or the host offline, Paseo
falls back to drafting and says so on screen. EVA cannot distinguish the two
outcomes, so the receipt says the send was requested, not delivered.

There is no `send` for a new agent: creating one goes through Paseo's New
workspace form (project, model, isolation), which a link cannot fill.

## What the package cannot do

Paseo exposes no read interface an EVA package can call: no content provider
and no HTTP API reachable from the phone without the app's pairing secrets.
The package therefore cannot list agents, workspaces, or hosts, and the model
has to learn IDs from the user or from a prior conversation. Listing and status
reads belong to EVA's installed-app AIDL protocol, which Paseo does not ship
yet.
