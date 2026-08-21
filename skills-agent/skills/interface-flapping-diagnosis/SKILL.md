---
name: interface-flapping-diagnosis
description: Diagnoses a reported flapping, unstable, or error-prone interface on a device that is otherwise reachable, by reading its error-counter pattern to tell a physical-layer problem apart from a congestion/duplex problem. Use when the user says an interface is flapping, dropping, erroring, or unstable — not for a fully unreachable device (see device-triage).
---

# Interface Flapping Diagnosis

The same symptom report ("Gi1/0/3 keeps flapping") can mean a bad cable, a
duplex mismatch, or congestion — and those have different fixes. Don't
recommend a fix based on the word "flapping" alone; the error counters tell
you which one it actually is.

## Workflow

1. **Confirm the device is reachable**, not down. Call `ping_device(hostname)`.
   If it's unreachable, this isn't an interface-flapping case at all — switch
   to the `device-triage` skill instead.
2. **Read the counters.** Call `check_interface_status(hostname, interface)`
   and look at the `errors` field:
   - **High `crc_errors`, low `input_drops`** → almost always a physical-layer
     problem: bad cable, dirty/failing transceiver, or a bent pin.
     Recommend reseating or replacing the cable/transceiver first — this is
     the cheapest thing to try and fixes most CRC-error cases.
   - **High `input_drops`, low `crc_errors`** → usually congestion or a
     duplex/speed mismatch, not a physical fault. Recommend checking
     configured speed/duplex on both ends match, and whether traffic volume
     alone explains the drops (if so, see the `capacity-check` skill).
   - **Both near zero** → the interface looks clean right now. Flapping is
     often intermittent, so say that plainly instead of inventing a cause —
     recommend checking device syslog/event history for the actual flap
     timestamps, which these tools don't provide.
3. **State your reasoning**, not just a conclusion — tell the user which
   counter drove the diagnosis (e.g. "1,842 CRC errors with no input drops
   points to the cable/transceiver, not congestion").

## Discipline

- Never recommend a duplex/config fix based on CRC errors, or a cable swap
  based on drops with clean CRCs — matching the wrong fix to the wrong
  counter pattern is worse than saying "inconclusive."
- If you already read this interface's counters earlier in the
  conversation, reuse them instead of calling `check_interface_status` again.
