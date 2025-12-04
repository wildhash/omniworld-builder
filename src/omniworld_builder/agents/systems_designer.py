"""Systems Designer Agent for designing gameplay mechanics and interactions."""

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from omniworld_builder.agents.base import AgentState, BaseAgent


class SystemsDesignerAgent(BaseAgent):
    """Agent responsible for designing gameplay mechanics and interactions.

    The Systems Designer creates the interactive layer of the world including
    physics rules, gameplay mechanics, user interactions, and system behaviors.
    """

    def __init__(self, model_name: str = "claude-sonnet-4-20250514") -> None:
        """Initialize the Systems Designer agent."""
        super().__init__(name="SystemsDesigner", model_name=model_name)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Systems Designer."""
        return """You are the Systems Designer, an expert in gameplay mechanics and interactive systems.
Your role is to design the interactive layer of 3D worlds based on the visual concept.

You must create a structured JSON output with:
1. physics_settings: Gravity, collision rules, material properties
2. interaction_systems: User interaction types and triggers
3. gameplay_mechanics: Core mechanics, objectives, progression
4. dynamic_elements: Moving objects, AI behaviors, procedural elements
5. audio_systems: Sound triggers, ambient audio, music zones
6. spawn_systems: Entity spawning rules and locations
7. event_triggers: Conditional events and their responses

Consider the visual concept provided and ensure systems complement the aesthetics.
Output ONLY valid JSON, no additional text."""

    async def process(self, state: AgentState) -> AgentState:
        """Process the vision output and generate systems design.

        Args:
            state: The current agent state with vision output.

        Returns:
            Updated state with systems output.
        """
        context = f"""
User Request: {state.user_prompt}

Visual Concept:
{state.vision_output}

Design interactive systems that complement this visual concept.
"""
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=context),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            systems_output = self._parse_response(response.content)
            state.systems_output = systems_output
            state.current_stage = "systems_complete"
        except Exception as e:
            state.errors.append(f"SystemsDesigner error: {str(e)}")
            state.systems_output = self._get_default_systems()

        return state

    def _parse_response(self, content: str) -> dict[str, Any]:
        """Parse the LLM response into structured output."""
        import json

        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except json.JSONDecodeError:
            return self._get_default_systems()

    def _get_default_systems(self) -> dict[str, Any]:
        """Return default systems output on error."""
        return {
            "physics_settings": {
                "gravity": {"x": 0, "y": -9.81, "z": 0},
                "collision_enabled": True,
                "physics_materials": ["default"],
            },
            "interaction_systems": [
                {"type": "click", "response": "select"},
                {"type": "proximity", "response": "highlight"},
            ],
            "gameplay_mechanics": {
                "type": "exploration",
                "objectives": [],
            },
            "dynamic_elements": [],
            "audio_systems": {
                "ambient_zones": [],
                "sound_triggers": [],
            },
            "spawn_systems": {
                "spawn_points": [],
                "spawn_rules": [],
            },
            "event_triggers": [],
        }
