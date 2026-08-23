# Python Host Capability Broker Protocol 1.5

Status: implemented in the current Host and Plugin development trees. The first
capability slice is toast, clipboard and application launch/navigation. Its
public engine path passed one API 31 arm64 physical-device smoke and one API 37
x86_64 16 KiB-page emulator smoke on 2026-08-23. This document describes the
reusable broker contract; it does not claim that later Roadmap capability
batches, a complete device matrix or a published release already exist.

## Negotiation and Binder compatibility

Provider metadata advertises protocol range `1.0-1.5` and
`supportsHostCapabilityBroker=true`. A Host may select the live broker only
when the negotiated protocol is at least 1.5 and the Provider advertises that
flag.

`IPythonRuntimeProvider.openSession` retains its historical AIDL order and is
used for protocol 1.0 through 1.4. Protocol 1.5 appends
`openSessionWithHostCapabilities(request, descriptors, broker,
admissionCallback, executionCallback)`. The Provider rejects a 1.5 request
without exactly one live broker and rejects a pre-1.5 request which attempts to
supply one. This preserves existing Binder transaction numbers and prevents a
new request from silently running without its live capability channel.

The Host-generated `python-runtime-api.aar` is the authority for the AIDL and
tagged metadata model. The Plugin locks the exact AAR SHA-256 and the clean Host
distribution manifest in `locks/host-api-aars.lock`.

## Execution binding and lifecycle

There is one broker per admitted execution:

1. The Host constructs the broker with the execution request UUID, the exact
   plugin UID pinned during provider discovery, and the enabled capability set.
2. The Host opens the session through the protocol 1.5 AIDL method.
3. The Plugin links the broker Binder to the same death handling used by its
   admission and execution callbacks, then gives the bootstrap one private
   `dispatch(String) -> String` bridge.
4. The bootstrap installs an execution-local Python client immediately before
   user code and removes it in `finally` while restoring all other interpreter
   state.
5. Host terminal, cancellation, callback loss, setup failure or client cleanup
   closes the Host dispatcher. Plugin terminal, cancellation, broker death or
   service/session cleanup closes the private bridge.
6. Calls admitted before cancellation may have performed their Host side
   effect, but are never replayed. Calls after close fail with
   `CapabilityUnavailableError` or a stable closed-broker response.

The Python client serializes an entire request/response exchange with one
execution-local lock. Call IDs therefore increase from 1 without duplicates,
and cleanup waits for an in-flight exchange before revoking copied
`contextvars` contexts.

## Strict JSON wire format

Both directions are non-empty strict UTF-8 JSON objects. The Python client emits
canonical requests with unique fields and rejects duplicate response fields.
Malformed values, missing fields, extra fields and mismatched execution/call IDs
are rejected at the receiving boundary.

Request:

```json
{
  "arguments": {"text": "hello"},
  "callId": 1,
  "capability": "toast.show",
  "executionId": "12345678-1234-5678-9abc-def012345678",
  "version": 1
}
```

Success:

```json
{
  "callId": 1,
  "executionId": "12345678-1234-5678-9abc-def012345678",
  "ok": true,
  "value": null,
  "version": 1
}
```

Failure:

```json
{
  "callId": 1,
  "error": {"code": "INVALID_ARGUMENT", "message": "Host capability arguments are invalid"},
  "executionId": "12345678-1234-5678-9abc-def012345678",
  "ok": false,
  "version": 1
}
```

The JSON document version is independent of the outer Python runtime protocol
version. Capability names use lowercase dotted identifiers. Arguments are an
exact object defined by the selected capability.

## Limits

| Limit | Value |
| --- | ---: |
| Calls admitted per execution | 1024 |
| Encoded request | 64 KiB |
| Encoded response | 64 KiB |
| One text argument | 32 KiB UTF-8 |
| One Host main-thread action wait | 5 s |

The overall Python execution deadline still applies independently. Exhausting
the call quota does not extend that deadline.

## Stable errors

The Host dispatcher can return:

| Code | Meaning |
| --- | --- |
| `CAPABILITY_UNAVAILABLE` | The method is unknown or was not granted |
| `INVALID_ARGUMENT` | Exact argument fields, text bounds, package name or URL shape failed |
| `HOST_FAILURE` | The existing Host action failed without exposing internal details |
| `HOST_TIMEOUT` | Dispatch to the Host main thread exceeded 5 seconds |
| `BROKER_CLOSED` | The execution-scoped dispatcher is already closed |
| `REPLAYED_CALL` | A positive call ID was reused |
| `CALL_LIMIT_EXCEEDED` | The execution consumed all 1024 calls |
| `RESULT_LIMIT_EXCEEDED` | The encoded Host result exceeded 64 KiB |

`CAPABILITY_UNAVAILABLE` and `BROKER_CLOSED` become
`autojs6.CapabilityUnavailableError`. Other Host failures become
`autojs6.HostCapabilityError`; its public `code` attribute contains the stable
code. A dead Binder, closed private bridge or missing negotiated broker becomes
`CapabilityUnavailableError`. A malformed/mismatched response becomes
`HostCapabilityError` with code `BROKER_PROTOCOL_ERROR`.

## Current Python facade

| Python API | Capability | Arguments | Result |
| --- | --- | --- | --- |
| `autojs6.toast(text: str) -> None` | `toast.show` | `{"text": text}` | `null` |
| `autojs6.clip.get() -> str` | `clip.get` | `{}` | clipboard text or `""` |
| `autojs6.clip.set(text: str) -> None` | `clip.set` | `{"text": text}` | `null` |
| `autojs6.app.launch(package_name: str) -> bool` | `app.launch` | `{"package": package_name}` | whether an activity launched |
| `autojs6.app.launch_app(name: str) -> bool` | `app.launch_app` | `{"name": name}` | whether an application label resolved and launched |
| `autojs6.app.open_url(url: str) -> bool` | `app.open_url` | `{"url": url}` | whether an activity accepted the URL |

Package names must use ordinary dotted Android identifier segments. URLs must
start with `http://` or `https://`. Empty toast/clipboard text is allowed;
package, application name and URL text must be non-empty.

The launch-time `app.snapshot()` and `device.snapshot()` APIs remain detached
immutable snapshots. The broker does not change project workspace semantics,
grant arbitrary files, expose a general Java bridge, or add dynamic device,
console, notification, accessibility, screenshot or OCR APIs. Those are
separate Roadmap items.

## Trust boundary

Python scripts are trusted local code for every permission and API they can
reach. Protocol 1.5 narrows the accidental cross-process surface but does not
turn Chaquopy into a hostile-code sandbox. User globals receive Python
functions, never Android `Context`, Host `ScriptRuntime`, callbacks or the raw
broker Binder. The Host validates the Binder calling UID before clearing its
identity, dispatches only an explicit allow-list, and replaces unexpected Host
exceptions with stable errors.

## Focused public-engine acceptance

`PythonU1R2AcceptanceInstrumentationTest#firstLowRiskHostCapabilitiesRoundTripThroughProtocol15Broker`
launches an admitted Python project through the ordinary Host script engine and
the real plugin. The script shows a toast, writes and reads a unique clipboard
marker, receives `False` for missing package/application launch targets, and
observes `INVALID_ARGUMENT` for an intentionally unsupported `ftp://` URL
without opening an external activity. A strict structured result proves the
round-trip values, the test restores the original Android `ClipData`, and the
normal project/private-snapshot cleanup is asserted.

The test passed on Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages)
in 1.607 seconds and on an API 37 x86_64 emulator with 16 KiB pages in 7.183
seconds. Both reported `OK (1 test)`. These are focused current-tree smokes, not
release or full-device-matrix evidence.
