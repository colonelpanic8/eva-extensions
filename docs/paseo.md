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

## Where the IDs come from

`list_workspaces` and `list_agents` are `android.content` reads of Paseo's
provider at `content://sh.paseo.assistant/{workspaces,agents}` with typed `q`,
`workspaceId`, and `limit` query slots. Paseo publishes the catalog behind
them while it is open, so rows are as fresh as the last time the app was in
the foreground; a workspace created since then is missing until Paseo opens
again. The provider exports no dangerous permission and gates callers to
EVA's package itself, so no device permission setup is needed; EVA's manifest
lists the authority for package visibility. The intended flow is list, pick an
`id`, then hand it to `open_workspace`, `open_agent`, `get_recent_messages`,
or the prompt capabilities. A debug build of Paseo uses `sh.paseo.debug.assistant` and is
not reachable from this package.

## Reading recent messages

`get_recent_messages` reads `content://sh.paseo.assistant/messages` with typed
`agentId`, `workspaceId`, and `limit` query slots and projects `id`, `serverId`,
`workspaceId`, `agentId`, `agentName`, `kind`, `createdAt`, and `text`, most
recent first. Exactly one of `agentId` and `workspaceId` has to be given, and
`agentId` wins when both are. With `workspaceId` the provider fans out over the
workspace's non-archived top-level agents, at most the six most recently
active, and merges their messages into one ordered list, so `agentName` is what
tells them apart; a workspace with no such agents returns zero rows. `limit` is
1–50 and Paseo defaults to 10.
EVA's input-schema subset has no `oneOf`, so both identifiers are optional in
the tool schema and the rule is stated in the description instead.

Unlike `list_workspaces` and `list_agents`, these rows are not read from the
published catalog. The provider asks the Paseo daemon for them at query time,
which is the point: a snapshot cannot say what an agent is doing now. The Paseo
app process therefore has to be alive and its host reachable. The capability
declares a 10-second deadline for a provider that can take about seven seconds.

When Paseo cannot answer — the app is not running, the host is offline, the id
is unknown, or the daemon times out — the provider does not throw. It returns a
single row whose `kind` is `notice` and whose `text` says what happened and what
the user can do, so the read still completes with something to report. The other
`kind` values are `user`, `assistant`, and `tool`; reasoning, todo lists, agent
errors, and notifications are not rows at all.

`text` is plain text clipped to 1,000 characters (a `tool` row is a one-line
summary of at most 200), and only the requested window is reachable; there is
no paging back through a session from here. Hand the user to `open_agent` to
read a full message or the rest of the history.

When the user names a workspace by what it is doing rather than by id, the flow
is two steps: `list_workspaces` with `q` (or `list_agents`) to get the `id`,
then `get_recent_messages` with it.
