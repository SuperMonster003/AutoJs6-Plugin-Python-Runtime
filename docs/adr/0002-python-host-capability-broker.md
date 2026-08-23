# ADR 0002: execution-scoped Python Host capability broker

Status: Accepted, 2026-08-23

## Context

The initial Python integration intentionally exposed only immutable launch-time
snapshots. That was enough to execute Python reliably, but it could not perform
ordinary AutoJs6 actions such as showing a toast, reading the Host clipboard or
launching an application. Lua already demonstrated an execution-bound broker
model, while Node.js demonstrated the breadth of Host APIs which can eventually
be represented as pure data.

Sending Android `Context`, `ScriptRuntime`, arbitrary Java objects or a general
Binder handle into user code would couple Python to Host internals and make
lifetime enforcement difficult. Taking a fresh snapshot for every action would
not support mutations and would be unnecessarily expensive.

## Decision

Protocol 1.5 adds `IPythonHostCapabilityBroker.dispatch(byte[]) -> byte[]` and
an appended `openSessionWithHostCapabilities` provider method. The old
`openSession` transaction remains unchanged for protocol 1.0 through 1.4.

The broker is created by the Host for exactly one Python execution and is bound
to both that execution's request UUID and the pinned plugin UID. Requests and
responses are strict, bounded UTF-8 JSON. Calls carry a positive per-execution
monotonic ID, have a finite quota, and are synchronous. The Host closes the
broker on every terminal, cancellation and setup-failure path. The Plugin links
the broker Binder to death and revokes its private Chaquopy bridge during every
session cleanup path.

User Python receives ordinary functions in `autojs6`, not Host objects. The
private bridge exposes only one `dispatch(str) -> str` method to the bootstrap.
The first capability set is deliberately small:

- `toast.show`;
- `clip.get` and `clip.set`;
- `app.launch`, `app.launch_app` and `app.open_url`.

The Host uses its existing `ScriptToast`, `ClipboardUtils` and `AppUtils`
implementations. Future capability batches reuse this protocol and dispatcher;
they do not require another provider Binder method merely to add a method name.

## Boundary and consequences

This is an intentional expansion of what a trusted local Python script can ask
the Host to do. It is not a hostile-code sandbox and is not an authorization
boundary between the script author and AutoJs6. The broker nevertheless limits
accidental lifetime leaks and malformed cross-process calls:

- the Host checks the calling UID before clearing Binder identity;
- exact request fields, execution ID, call ID, capability grant and argument
  shapes are validated before dispatch;
- each execution permits at most 1024 calls, each request and response is at
  most 64 KiB, text arguments are at most 32 KiB, and a Host main-thread action
  waits at most 5 seconds;
- duplicate call IDs, calls after close, unsupported methods and invalid
  arguments return stable error codes;
- arbitrary Host exceptions are reduced to stable messages rather than crossing
  the boundary with internal details.

The Python facade is blocking. A long-running script should call it from normal
script control flow and must not assume that an Android UI action is immediate.
Copied Python contexts are revoked when execution cleanup closes their shared
broker state. Calls which were already dispatched are not replayed.

The complete data and lifecycle contract is documented in
[`docs/python/HOST_CAPABILITY_BROKER_PROTOCOL.md`](../python/HOST_CAPABILITY_BROKER_PROTOCOL.md).
