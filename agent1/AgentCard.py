from a2a.types import AgentCard, AgentSkill

agent_card = AgentCard(
    id="agent1-email",
    name="Email Agent",
    description="Agent that sends emails via Gmail API.",
    version="1.0.0",
    url="http://agent1:8000",
    capabilities={"streaming": False},
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(
            id="send_email",
            name="Send Email",
            description="Capable of sending emails to any address with a custom subject and body.",
            tags=["email", "communication"],
            examples=["Send an email to john@example.com saying hi"]
        )
    ]
)
