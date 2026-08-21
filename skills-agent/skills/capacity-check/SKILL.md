---
name: capacity-check
description: Checks whether a device's interface is running near its bandwidth capacity and whether an upgrade is warranted. Use when the user asks about capacity, bandwidth headroom, link saturation, or whether an interface/uplink needs upgrading.
---

# Capacity Check

Utilization alone can be misleading — high numbers sometimes come from
retransmits caused by an error condition, not genuine traffic growth. Rule
that out before recommending a costly upgrade.

## Workflow

1. **Confirm the device is reachable.** Call `ping_device(hostname)`. If
   it's unreachable, switch to the `device-triage` skill instead — you can't
   get meaningful utilization data from a device that's down.
2. **Get utilization.** Call `get_interface_utilization(hostname, interface)`.
3. **Apply thresholds:**
   - `> 85%` sustained → upgrade candidate now; recommend scheduling the
     upgrade.
   - `60–85%` → healthy for now but worth planning for the next capacity
     cycle; note it, don't recommend immediate action.
   - `< 60%` → no capacity concern.
4. **Rule out errors before concluding it's genuine growth.** Call
   `check_interface_status(hostname, interface)`. If `crc_errors` or
   `input_drops` are also elevated, say so explicitly and point to the
   `interface-flapping-diagnosis` skill — fixing the error condition first
   is cheaper than an upgrade, and might resolve the utilization reading
   too (retransmits inflate observed utilization).

## Discipline

- Always report the actual percentage and which threshold band it falls
  into — don't just say "high" or "fine."
- Don't skip step 4 even if utilization alone looks clearly high or clearly
  low; the error check is what separates "genuine capacity problem" from
  "error condition masquerading as one."
