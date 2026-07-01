# cisco-switch-agent

An NCP agent that SSHes into Cisco switches and reports **inventory**, **health**,
and **traffic** using read-only `show` commands. Switch credentials
(`mgmtIP`, `username`, `password`) are read from a **devices file** — the agent
never asks the user for them.

Supports Cisco **IOS**, **IOS-XE**, **NX-OS**, and **IOS-XR** (via Netmiko).

## What it does

| Ask | Tool | Show commands (IOS / NX-OS) |
|-----|------|------------------------------|
| "What switches do you manage?" | `list_devices` | — |
| Inventory / model / serial / version | `get_inventory` | `show version`, `show inventory`, `show module` |
| Health / CPU / memory / power / temp | `get_health` | `show processes cpu`, `show processes memory`, `show environment`, `show system resources` |
| Traffic / interfaces / counters / errors | `get_traffic` | `show interfaces summary`, `show interfaces counters`, `show interface counters errors` |
| Anything else | `run_show_command` | any single `show ...` command |

All tools are strictly **read-only** — `run_show_command` rejects anything that
is not a `show` command, and no configuration commands are ever issued.

## Devices file

Credentials live in `devices.yaml` (copy `devices.yaml.example` to start):

```yaml
devices:
  - name: core-sw1
    mgmtIP: 10.4.4.61
    username: admin
    password: "your-password"
    device_type: cisco_ios     # cisco_ios | cisco_xe | cisco_nxos | cisco_xr
  - name: core-sw2
    mgmtIP: 10.4.4.62
    username: admin
    password: "your-password"
    device_type: cisco_nxos
```

Optional per-device fields: `secret` (enable password) and `port` (default 22).

- The agent locates the file next to the project, or at `$CISCO_DEVICES_FILE`.
- `devices.yaml` is **git-ignored** so plaintext passwords never get committed.
  Only `devices.yaml.example` is tracked.

## Setup

```bash
cd cisco-switch-agent
cp devices.yaml.example devices.yaml   # then edit with real IPs/credentials
pip install -r requirements.txt        # netmiko, pyyaml
```

## Run

Point the agent at your NCP platform in `ncp.toml`, then deploy/run it with the
`ncp` CLI as with the other examples in this repo.

### Example prompts

- "List the switches you manage."
- "Show me the inventory for all switches."
- "Is core-sw1 healthy? Check CPU and memory."
- "Show interface traffic and errors on 10.4.4.62."
- "Run `show ip interface brief` on core-sw1."

## How it works

- `tools/cisco_tools.py` — loads the devices file, resolves a target switch by
  name or `mgmtIP`, opens a Netmiko SSH session, runs the platform-appropriate
  `show` commands, and returns raw output per device.
- `agents/main_agent.py` — the agent that selects the right tool, parses the raw
  output, and presents inventory/health/traffic summaries. It is instructed to
  ground every fact in tool output (zero hallucinations) and to surface tool
  errors verbatim.

## Notes

- Credentials never leave the devices file; the agent only reads `mgmtIP`,
  `username`, and `password` to open the SSH session.
- If a switch is unreachable or credentials are wrong, the tool returns an
  `error` field and the agent reports it rather than inventing data.
