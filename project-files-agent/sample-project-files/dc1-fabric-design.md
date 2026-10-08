# DC1 Fabric Design Standard

Owner: Network Engineering. Applies to every device in the DC1 data center.

## Topology

DC1 is a two-tier leaf-spine fabric. Two spines (`spine-01`, `spine-02`)
connect to every leaf. Leaves are deployed in pairs per rack row; each server
is dual-homed to a leaf pair with MLAG (Arista) or vPC (Cisco).

The border leaves (`bleaf-01`, `bleaf-02`) carry all north-south traffic and
peer with the WAN edge routers.

## Routing

- The underlay is eBGP. Spines share AS **65000**. Each leaf has its own
  private AS, starting at **65101** for `leaf-01` and incrementing by one.
- BFD is enabled on every underlay session with a 300 ms interval and a
  multiplier of 3.
- The overlay is EVPN/VXLAN. Spines act as route servers; leaves are VTEPs.

## MTU

All fabric links run an MTU of **9214** bytes. Server-facing ports run 9000.
A fabric link at a lower MTU is a design violation and must be fixed in the
next maintenance window.

## Software standard

Every device must run the approved release for its vendor:

| Vendor | Approved release |
|---|---|
| Arista | EOS 4.32.2F |
| Cisco | NX-OS 10.4(3) |

A device on any other release is non-compliant and needs an upgrade ticket.

## Lifecycle policy

A device must be replaced before its vendor end-of-life (EOL) date. Devices
within **180 days** of EOL go on the refresh list for the next budget cycle.
A device already past EOL is a P1 risk and must be raised with the
infrastructure manager.

## Change management

- The standard maintenance window is **Sunday 02:00–04:00 UTC**.
- Spine changes need two approvers from Network Engineering.
- Never change both members of a leaf pair in the same window.
