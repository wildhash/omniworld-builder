"""Multi-agent orchestrator using LangGraph for world building."""

from typing import Any, Literal

from langgraph.graph import END, StateGraph

from omniworld_builder.agents.base import AgentState
from omniworld_builder.agents.qa_agent import QAAgent
from omniworld_builder.agents.systems_designer import SystemsDesignerAgent
from omniworld_builder.agents.technical_director import TechnicalDirectorAgent
from omniworld_builder.agents.vision_architect import VisionArchitectAgent
from omniworld_builder.agents.wdl_generator import WDLGeneratorAgent
from omniworld_builder.core.wdl_schema import WDLWorld


class WorldBuilderOrchestrator:
    """Orchestrates the multi-agent world building pipeline using LangGraph.

    The orchestrator manages the flow between agents:
    1. Vision Architect - Creates visual concept
    2. Systems Designer - Designs gameplay mechanics
    3. Technical Director - Creates technical specs
    4. WDL Generator - Generates the WDL world
    5. QA Agent - Validates and approves or requests revision
    """

    def __init__(self, model_name: str = "claude-sonnet-4-20250514") -> None:
        """Initialize the orchestrator with all agents.

        Args:
            model_name: The LLM model to use for all agents.
        """
        self.model_name = model_name
        self.vision_agent = VisionArchitectAgent(model_name)
        self.systems_agent = SystemsDesignerAgent(model_name)
        self.technical_agent = TechnicalDirectorAgent(model_name)
        self.wdl_agent = WDLGeneratorAgent(model_name)
        self.qa_agent = QAAgent(model_name)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        # Create the state graph with AgentState schema
        workflow = StateGraph(AgentState)

        # Add nodes for each agent
        workflow.add_node("vision", self._vision_node)
        workflow.add_node("systems", self._systems_node)
        workflow.add_node("technical", self._technical_node)
        workflow.add_node("wdl_generator", self._wdl_node)
        workflow.add_node("qa", self._qa_node)

        # Define the workflow edges
        workflow.set_entry_point("vision")
        workflow.add_edge("vision", "systems")
        workflow.add_edge("systems", "technical")
        workflow.add_edge("technical", "wdl_generator")
        workflow.add_edge("wdl_generator", "qa")

        # Add conditional edge from QA - either end or loop back
        workflow.add_conditional_edges(
            "qa",
            self._should_continue,
            {
                "continue": "vision",  # Loop back for revision
                "end": END,
            },
        )

        return workflow.compile()

    async def _vision_node(self, state: AgentState) -> dict[str, Any]:
        """Execute the Vision Architect agent."""
        updated_state = await self.vision_agent.process(state)
        return {
            "vision_output": updated_state.vision_output,
            "current_stage": updated_state.current_stage,
            "errors": updated_state.errors,
        }

    async def _systems_node(self, state: AgentState) -> dict[str, Any]:
        """Execute the Systems Designer agent."""
        updated_state = await self.systems_agent.process(state)
        return {
            "systems_output": updated_state.systems_output,
            "current_stage": updated_state.current_stage,
            "errors": updated_state.errors,
        }

    async def _technical_node(self, state: AgentState) -> dict[str, Any]:
        """Execute the Technical Director agent."""
        updated_state = await self.technical_agent.process(state)
        return {
            "technical_output": updated_state.technical_output,
            "current_stage": updated_state.current_stage,
            "errors": updated_state.errors,
        }

    async def _wdl_node(self, state: AgentState) -> dict[str, Any]:
        """Execute the WDL Generator agent."""
        updated_state = await self.wdl_agent.process(state)
        return {
            "wdl_output": updated_state.wdl_output,
            "current_stage": updated_state.current_stage,
            "errors": updated_state.errors,
        }

    async def _qa_node(self, state: AgentState) -> dict[str, Any]:
        """Execute the QA agent."""
        updated_state = await self.qa_agent.process(state)
        return {
            "qa_output": updated_state.qa_output,
            "current_stage": updated_state.current_stage,
            "errors": updated_state.errors,
            "is_complete": updated_state.is_complete,
            "iteration_count": state.iteration_count + 1,
        }

    def _should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """Determine if the workflow should continue or end."""
        if state.is_complete:
            return "end"
        if state.iteration_count >= state.max_iterations:
            return "end"
        # Check if QA approved
        if state.qa_output.get("approval", False):
            return "end"
        return "continue"

    async def build_world(self, prompt: str, max_iterations: int = 5) -> WDLWorld:
        """Build a world from a natural language prompt.

        Args:
            prompt: Natural language description of the desired world.
            max_iterations: Maximum number of revision cycles.

        Returns:
            Generated WDLWorld object.
        """
        initial_state = AgentState(
            user_prompt=prompt,
            max_iterations=max_iterations,
        )

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)

        # Extract the WDL world from the final state
        wdl_data = final_state.get("wdl_output", {}).get("wdl_world", {})
        return WDLWorld.model_validate(wdl_data)

    async def build_world_with_state(
        self, prompt: str, max_iterations: int = 5
    ) -> tuple[WDLWorld, AgentState]:
        """Build a world and return both the world and final state.

        Args:
            prompt: Natural language description of the desired world.
            max_iterations: Maximum number of revision cycles.

        Returns:
            Tuple of (WDLWorld, final AgentState).
        """
        initial_state = AgentState(
            user_prompt=prompt,
            max_iterations=max_iterations,
        )

        # Run the graph
        final_state_dict = await self.graph.ainvoke(initial_state)

        # Convert dict to AgentState
        final_state = AgentState(**final_state_dict)

        # Extract the WDL world
        wdl_data = final_state.wdl_output.get("wdl_world", {})
        world = WDLWorld.model_validate(wdl_data)

        return world, final_state
