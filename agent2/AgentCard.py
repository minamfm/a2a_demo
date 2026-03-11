from a2a.types import AgentCard, AgentSkill

agent_card = AgentCard(
    id="agent2-sheets",
    name="Spreadsheet Agent",
    description="Agent that creates Google Spreadsheets.",
    version="1.0.0",
    url="http://agent2:8000",
    capabilities={"streaming": False},
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(
            id="create_spreadsheet",
            name="Create Spreadsheet",
            description="Capable of creating new Google Spreadsheets with a given title.",
            tags=["spreadsheet", "google-sheets"],
            examples=["Create a spreadsheet for my weekly budget"]
        ),
        AgentSkill(
            id="append_spreadsheet_values",
            name="Append Spreadsheet Values",
            description="Capable of appending data to an existing Google Spreadsheet.",
            tags=["spreadsheet", "google-sheets", "append"],
            examples=["Add these items to my grocery list spreadsheet"]
        )
    ]
)
