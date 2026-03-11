from a2a.types import AgentCard, AgentSkill

agent_card = AgentCard(
    id="agent3-orchestrator",
    name="Orchestrator Agent",
    description="Agent that acts as a router to other agents based on user intent.",
    version="1.0.0",
    url="http://agent3:8000",
    capabilities={"streaming": False},
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(
            id="routing",
            name="Routing",
            description="Routes messages to appropriate agents",
            tags=["orchestration", "routing"]
        ),
        AgentSkill(
            id="coordination",
            name="Coordination",
            description="Coordinates tasks across multiple agents",
            tags=["orchestration", "coordination"]
        )
    ]
)
