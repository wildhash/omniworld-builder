"""Technical Director Agent for translating concepts to technical specifications."""

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from omniworld_builder.agents.base import AgentState, BaseAgent


class TechnicalDirectorAgent(BaseAgent):
    """Agent responsible for translating concepts to technical specifications.

    The Technical Director bridges the gap between creative vision and
    technical implementation, defining entity hierarchies, asset requirements,
    and platform-specific considerations.
    """

    def __init__(self, model_name: str = "claude-sonnet-4-20250514") -> None:
        """Initialize the Technical Director agent."""
        super().__init__(name="TechnicalDirector", model_name=model_name)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Technical Director."""
        return """You are the Technical Director, an expert in game engine architecture and technical implementation.
Your role is to translate creative concepts into technical specifications for game engines.

You must create a structured JSON output with:
1. entity_hierarchy: Parent-child relationships and scene structure
2. asset_requirements: List of 3D models, textures, materials needed
3. performance_budget: Target poly counts, texture sizes, draw calls
4. lod_strategy: Level of detail settings for optimization
5. platform_considerations: Unity, Unreal, Horizon-specific notes
6. shader_requirements: Custom shader needs and effects
7. optimization_notes: Performance recommendations

Consider both the visual concept and systems design when creating technical specs.
Ensure cross-platform compatibility where possible.
Output ONLY valid JSON, no additional text."""

    async def process(self, state: AgentState) -> AgentState:
        """Process vision and systems output to generate technical specs.

        Args:
            state: The current agent state with vision and systems output.

        Returns:
            Updated state with technical output.
        """
        context = f"""
User Request: {state.user_prompt}

Visual Concept:
{state.vision_output}

Systems Design:
{state.systems_output}

Create technical specifications for implementing this world across Unity, Unreal, and Horizon.
"""
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=context),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            technical_output = self._parse_response(response.content)
            state.technical_output = technical_output
            state.current_stage = "technical_complete"
        except Exception as e:
            state.errors.append(f"TechnicalDirector error: {str(e)}")
            state.technical_output = self._get_default_technical()

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
            return self._get_default_technical()

    def _get_default_technical(self) -> dict[str, Any]:
        """Return default technical output on error."""
        return {
            "entity_hierarchy": {
                "root": "World",
                "children": ["Environment", "Entities", "Lights", "Systems"],
            },
            "asset_requirements": {
                "models": [],
                "textures": [],
                "materials": [],
                "audio": [],
            },
            "performance_budget": {
                "target_fps": 60,
                "max_poly_count": 500000,
                "max_texture_memory_mb": 512,
                "max_draw_calls": 1000,
            },
            "lod_strategy": {
                "lod_levels": 3,
                "lod_distances": [50, 100, 200],
            },
            "platform_considerations": {
                "unity": {"render_pipeline": "URP"},
                "unreal": {"render_pipeline": "forward"},
                "horizon": {"optimization_level": "mobile"},
            },
            "shader_requirements": [],
            "optimization_notes": [],
        }
