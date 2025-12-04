"""Base agent class for all world-building agents."""

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """State shared between agents in the orchestration."""

    user_prompt: str = ""
    vision_output: dict[str, Any] = Field(default_factory=dict)
    systems_output: dict[str, Any] = Field(default_factory=dict)
    technical_output: dict[str, Any] = Field(default_factory=dict)
    wdl_output: dict[str, Any] = Field(default_factory=dict)
    qa_output: dict[str, Any] = Field(default_factory=dict)
    messages: list[BaseMessage] = Field(default_factory=list)
    current_stage: str = "initial"
    iteration_count: int = 0
    max_iterations: int = 5
    errors: list[str] = Field(default_factory=list)
    is_complete: bool = False


class BaseAgent(ABC):
    """Base class for all world-building agents."""

    def __init__(self, name: str, model_name: str = "claude-sonnet-4-20250514") -> None:
        """Initialize the base agent.

        Args:
            name: The name of the agent.
            model_name: The LLM model to use.
        """
        self.name = name
        self.model_name = model_name
        self._llm = None

    @property
    def llm(self):
        """Lazy initialization of the LLM."""
        if self._llm is None:
            from langchain_anthropic import ChatAnthropic

            self._llm = ChatAnthropic(model=self.model_name, temperature=0.7)
        return self._llm

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""

    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """Process the current state and return updated state.

        Args:
            state: The current agent state.

        Returns:
            Updated agent state.
        """

    def format_output(self, output: dict[str, Any]) -> str:
        """Format the agent output for display."""
        return f"[{self.name}] Output: {output}"
