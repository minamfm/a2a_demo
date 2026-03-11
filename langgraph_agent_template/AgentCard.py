from a2a.types import AgentCard, AgentSkill

# Define your agent's identity and capabilities
agent_card = AgentCard(
    id="template-agent",
    name="Template Agent",
    description="A template for LangGraph-based A2A compliant agents.",
    version="1.0.0",
    url="http://0.0.0.0:8000",
    capabilities={"streaming": False},
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(
            id="echo_skill",
            name="Echo Skill",
            description="A sample skill that echoes back the user input.",
            tags=["sample", "echo"],
            examples=["Echo: Hello World"]
        )
    ]
)
