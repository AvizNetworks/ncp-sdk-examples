---
name: device-triage
description: Structured workflow for confirming whether a device is up and reachable at all. Use this whenever the user reports a device may be down, unreachable, or unresponsive — not for a reachable device with a specific interface problem (see interface-flapping-diagnosis) or a bandwidth/capacity question (see capacity-check).
---

# Device Triage

A wrong order here wastes calls and can produce a misleading answer (e.g.
reporting interface errors for a device that's actually unreachable). Follow
these steps in order.

## Workflow

1. **Confirm the device exists.** Call `get_device_inventory(hostname)`.
   If `found` is `false`, stop and tell the user the device isn't in
   inventory — don't guess at vendor/model, and don't proceed to reachability
   or interface checks.
2. **Check reachability.** Call `ping_device(hostname)`.
   - If `reachable` is `false`, stop here. Report the device as down. Do
     **not** call `check_interface_status` — an unreachable device can't
     give you meaningful interface data, and the tool will just fail.
   - If `reachable` is `true`, continue.
3. **Synthesize a short triage summary**: device identity (vendor/model)
   and reachability. If the device is reachable and the user's actual
   question is about a specific interface's errors/flapping or about
   bandwidth/capacity, say so and switch to the appropriate skill
   (`interface-flapping-diagnosis` or `capacity-check`) rather than
   guessing at those from this workflow.

## When to skip this

If the user already told you the device is reachable, skip straight to
whichever more specific skill actually matches their question — this skill
exists only to answer "is the device itself up," not to route every request.

## Discipline

- Do this once per device per request. If you already confirmed a device's
  reachability earlier in this conversation, reuse that instead of
  re-running `ping_device`.
- Never present inventory/reachability data you didn't just get from a tool
  call in this request — these tools are the only source of truth here.
