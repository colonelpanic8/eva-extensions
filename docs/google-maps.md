# Google Maps package notes

`packages/google-maps.json` drives Google Maps through the Android intent schemes
Google documents for apps. EVA ships a byte-identical copy and installs it by
default; see EVA's `docs/extension-protocol.md` under *Shipped default packages*.

## Actions

| Tool | Intent data | Handler |
| --- | --- | --- |
| `search` | `geo:0,0?q=<destination>` | Any map app; Google Maps when installed |
| `navigate` | `google.navigation:q=<destination>&mode=<d\|b\|w\|l>` | Google Maps, or any app registered for `google.navigation` |

Neither action pins a package, so a phone without Google Maps still gets search
and navigation from whichever map app handles the scheme. Both are handoffs: the
receipt says the app opened, not that the user arrived.

`travelmode` is a closed enum (`driving`, `bicycling`, `walking`, `two-wheeler`)
in the tool schema; the binding's `values` map turns it into Google's `mode`
letters (`d`, `b`, `w`, `l`) so the model never sees the codes, and `driving` is
the default when the argument is omitted. EVA rejects any other value before
launching. Transit is not a `google.navigation` mode and is not offered.

The destination is a `{destination}` placeholder in the fixed intent data. It is
percent-encoded whole, so `Park &mode=w` stays inside `q=` and cannot add or
change a parameter.

## Verification

Codec decode, default grant adoption, and the exact launched intents (including
the default and explicit travel modes and an injected `&mode=`) are covered by
EVA's `GoogleMapsPackageTest`. A device run with Google Maps installed has not
been recorded yet.
