"""Main agent definition for skills-agent.

Deliberately minimal `instructions` — the three step-by-step diagnostic
procedures live entirely in skills/*/SKILL.md, not here, and are NOT
enumerated here either. That's the point of this example: `instructions`
are always loaded into every turn's system prompt, but the platform injects
an "## Available Skills" section itself (just each skill's name +
description, ~100 tokens each) — the full body of whichever *one* skill is
actually relevant only loads when the agent calls read_skill for it. Adding
a fourth or fifth skill costs this agent nothing extra per turn beyond one
more name+description line; it would cost real, permanent context on every
single turn if it were pasted into `instructions` instead. See this
project's README for the numbers.
"""

from ncp import Agent
from tools import (
    get_device_inventory,
    ping_device,
    check_interface_status,
    get_interface_utilization,
)


agent = Agent(
    name="SkillsAgent",
    description="A network device triage assistant that uses Agent Skills for its workflows",
    instructions="""
    You are a network device triage assistant. You have four tools for
    inspecting devices and several skills, each describing the correct
    procedure for one class of reported problem. Check your available
    skills for one matching the user's report, call read_skill on it, and
    follow its workflow before using any device tool.
    """,
    tools=[
        get_device_inventory,
        ping_device,
        check_interface_status,
        get_interface_utilization,
    ],
    skills=["device-triage", "interface-flapping-diagnosis", "capacity-check"],
)
