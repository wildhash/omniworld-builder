"""Vision Architect Agent for conceptualizing world aesthetics and visual design."""

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from omniworld_builder.agents.base import AgentState, BaseAgent


class VisionArchitectAgent(BaseAgent):
    """Agent responsible for conceptualizing world aesthetics and visual design.

    The Vision Architect interprets user prompts and creates a comprehensive
    visual concept including art style, color palette, lighting design,
    environmental aesthetics, and overall mood.
    """

    def __init__(self, model_name: str = "claude-sonnet-4-20250514") -> None:
        """Initialize the Vision Architect agent."""
        super().__init__(name="VisionArchitect", model_name=model_name)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Vision Architect."""
        return """You are the Vision Architect, an expert in visual design and world aesthetics.
Your role is to interpret user descriptions and create comprehensive visual concepts for 3D worlds.

You must analyze the user's request and output a structured JSON with the following:
1. art_style: The overall artistic style (realistic, stylized, cartoon, pixel, etc.)
2. color_palette: Primary and secondary colors with hex codes
3. mood: The emotional tone (serene, ominous, vibrant, mysterious, etc.)
4. lighting_design: Type of lighting, time of day, key light sources
5. environmental_elements: Key visual features (terrain, vegetation, structures)
6. atmospheric_effects: Weather, particles, fog, etc.
7. reference_inspirations: Similar worlds/games/media for reference

Output ONLY valid JSON, no additional text."""

    async def process(self, state: AgentState) -> AgentState:
        """Process the user prompt and generate visual concept.

        Args:
            state: The current agent state with user prompt.

        Returns:
            Updated state with vision output.
        """
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=f"Create a visual concept for: {state.user_prompt}"),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            vision_output = self._parse_response(response.content)
            state.vision_output = vision_output
            state.current_stage = "vision_complete"
        except Exception as e:
            state.errors.append(f"VisionArchitect error: {str(e)}")
            state.vision_output = self._get_default_vision()

        return state

    def _parse_response(self, content: str) -> dict[str, Any]:
        """Parse the LLM response into structured output."""
        import json

        try:
            # Try to extract JSON from the response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except json.JSONDecodeError:
            return self._get_default_vision()

    def _get_default_vision(self) -> dict[str, Any]:
        """Return default vision output on error."""
        return {
            "art_style": "realistic",
            "color_palette": {
                "primary": ["#4A90A4", "#2C5F2D"],
                "secondary": ["#97BC62", "#D4A574"],
            },
            "mood": "serene",
            "lighting_design": {
                "type": "natural",
                "time_of_day": "afternoon",
                "key_sources": ["sun", "ambient"],
            },
            "environmental_elements": ["terrain", "vegetation", "sky"],
            "atmospheric_effects": ["light_fog", "dust_particles"],
            "reference_inspirations": [],
        }
