# Web, Email, Calendar, and Settings

These four packages carry the stock Android actions EVA used to implement in
Kotlin. EVA ships byte-identical copies and installs them by default; a user can
remove any of them and the removal follows their configuration.

| Package | Tool | Intent |
| --- | --- | --- |
| Web | `search` | `android.intent.action.WEB_SEARCH` with the `query` extra |
| Web | `open` | `android.intent.action.VIEW` on the given `http`/`https` URL, `httpUrl`-validated |
| Email | `compose` | `android.intent.action.SENDTO` on `mailto:<recipient>` with subject/body extras, `emailAddress`-validated |
| Calendar | `event` | `android.intent.action.INSERT` on the fixed `content://com.android.calendar/events` with title, location, description, and `beginTime`/`endTime` extras |
| Settings | `open` | The `screen` enum maps onto one of eleven `android.settings.*` actions |

Nothing is pinned to a package: Android offers whichever browser, mail, calendar,
or settings app handles the intent. Every action is a handoff; none reports a
result. `Web.open` is the only catalog binding where the request itself chooses
the destination, which is what opening an address means; the scheme allowlist
and validator keep it to web addresses.

`Calendar.event` takes explicit start and end times in Unix milliseconds. Supply
both when the time is known; with only a start, the calendar app applies its own
default length. The lower bound on both is 2000-01-01 so an accidental small
number cannot be handed over as a 32-bit extra.

## Verification

Codec decode, default adoption, and the exact launched intents (including the
rejection of `javascript:` and `intent:` URLs, an email recipient carrying a
query, and an unknown settings screen) are covered by EVA's `StockPackagesTest`.
No device run has been recorded yet.
