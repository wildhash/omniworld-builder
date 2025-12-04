"""QA Agent for validating and quality-checking generated worlds."""

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from omniworld_builder.agents.base import AgentState, BaseAgent
from omniworld_builder.core.validators import ValidationSeverity, WDLValidator
from omniworld_builder.core.wdl_schema import WDLWorld


class QAAgent(BaseAgent):
    """Agent responsible for quality assurance and validation.

    The QA Agent reviews the generated WDL world and validates it against
    quality standards, technical requirements, and user expectations.
    """

    def __init__(self, model_name: str = "claude-sonnet-4-20250514") -> None:
        """Initialize the QA agent."""
        super().__init__(name="QAAgent", model_name=model_name)
        self.validator = WDLValidator()

    def get_system_prompt(self) -> str:
        """Get the system prompt for the QA Agent."""
        return """You are the QA Agent, an expert in quality assurance for 3D world generation.
Your role is to validate generated worlds against quality standards and user requirements.

Review the generated WDL world and provide feedback on:
1. completeness: Does the world fulfill the user's original request?
2. consistency: Are visual, systems, and technical elements aligned?
3. performance: Are there any performance concerns?
4. improvements: Suggested enhancements or additions
5. issues: Any problems that need to be addressed
6. approval: Whether the world is ready for export (true/false)
7. score: Quality score from 0-100

Be constructive but thorough in your assessment.
Output ONLY valid JSON, no additional text."""

    async def process(self, state: AgentState) -> AgentState:
        """Process the WDL output and perform quality validation.

        Args:
            state: The current agent state with WDL output.

        Returns:
            Updated state with QA output.
        """
        # First, run structural validation
        wdl_data = state.wdl_output.get("wdl_world", {})
        structural_issues = []

        try:
            # Reconstruct WDL world for validation
            wdl_world = WDLWorld.model_validate(wdl_data)
            validation_result = self.validator.validate(wdl_world)

            for issue in validation_result.issues:
                structural_issues.append(
                    {
                        "severity": issue.severity.value,
                        "message": issue.message,
                        "entity_id": issue.entity_id,
                        "field": issue.field_path,
                    }
                )
        except Exception as e:
            structural_issues.append(
                {"severity": "error", "message": f"Failed to validate WDL: {str(e)}"}
            )

        # Then, run LLM-based quality assessment
        context = f"""
User Request: {state.user_prompt}

Visual Concept Summary:
- Art Style: {state.vision_output.get('art_style', 'unknown')}
- Mood: {state.vision_output.get('mood', 'unknown')}

Systems Design Summary:
- Physics: {state.systems_output.get('physics_settings', {})}
- Interactions: {len(state.systems_output.get('interaction_systems', []))} systems

Generated WDL World:
- Title: {wdl_data.get('metadata', {}).get('title', 'unknown')}
- Entities: {len(wdl_data.get('entities', []))} entities
- Lights: {len(wdl_data.get('lights', []))} lights
- Systems: {len(wdl_data.get('systems', []))} systems

Structural Validation Issues:
{structural_issues}

Assess the quality of this generated world.
"""
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=context),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            qa_output = self._parse_response(response.content)
            qa_output["structural_issues"] = structural_issues
            state.qa_output = qa_output

            # Determine if world is ready
            has_errors = any(
                issue["severity"] == ValidationSeverity.ERROR.value for issue in structural_issues
            )
            is_approved = qa_output.get("approval", False) and not has_errors

            state.is_complete = is_approved or state.iteration_count >= state.max_iterations
            state.current_stage = "qa_complete"

        except Exception as e:
            state.errors.append(f"QAAgent error: {str(e)}")
            state.qa_output = self._get_default_qa(structural_issues)
            state.is_complete = True  # End on error

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
            return self._get_default_qa([])

    def _get_default_qa(self, structural_issues: list[dict[str, Any]]) -> dict[str, Any]:
        """Return default QA output on error."""
        has_errors = any(issue.get("severity") == "error" for issue in structural_issues)
        return {
            "completeness": "Unable to assess",
            "consistency": "Unable to assess",
            "performance": "Unable to assess",
            "improvements": [],
            "issues": structural_issues,
            "approval": not has_errors,
            "score": 50 if not has_errors else 0,
            "structural_issues": structural_issues,
        }
