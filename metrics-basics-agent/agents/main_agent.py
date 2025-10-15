from ncp import Agent
from tools.metrics_tools import (
    get_device_inventory,
    check_device_status,
    list_interfaces,
    get_device_details,
)


agent = Agent(
    name="metrics-basics-agent",
    description="Network inventory assistant using the Metrics API for device queries",
    instructions="""You are a network inventory assistant""",
    tools=[
        get_device_inventory,
        check_device_status,
        list_interfaces,
        get_device_details,
    ],
)
