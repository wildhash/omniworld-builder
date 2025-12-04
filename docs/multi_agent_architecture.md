# Multi-Agent Architecture

OmniWorld Builder uses a multi-agent orchestration system powered by LangGraph to transform natural language descriptions into complete 3D worlds.

## Agent Overview

The system consists of five specialized agents that work together in a pipeline:

```
User Prompt → Vision Architect → Systems Designer → Technical Director → WDL Generator → QA Agent → WDL World
                     ↑                                                                        │
                     └────────────────────── Revision Loop ──────────────────────────────────┘
```

## Agents

### 1. Vision Architect

**Role**: Conceptualizes the visual design and aesthetics of the world.

**Responsibilities**:
- Interpret user descriptions
- Define art style (realistic, stylized, cartoon, etc.)
- Create color palette
- Design lighting concept
- Specify mood and atmosphere
- Identify environmental elements

**Output**:
```json
{
  "art_style": "realistic",
  "color_palette": {
    "primary": ["#4A90A4", "#2C5F2D"],
    "secondary": ["#97BC62", "#D4A574"]
  },
  "mood": "serene",
  "lighting_design": {
    "type": "natural",
    "time_of_day": "afternoon",
    "key_sources": ["sun", "ambient"]
  },
  "environmental_elements": ["terrain", "vegetation", "water"],
  "atmospheric_effects": ["fog", "particles"]
}
```

### 2. Systems Designer

**Role**: Designs gameplay mechanics and interactive systems.

**Responsibilities**:
- Define physics rules
- Design interaction systems
- Specify gameplay mechanics
- Plan dynamic elements
- Configure audio systems
- Set up spawn and trigger systems

**Output**:
```json
{
  "physics_settings": {
    "gravity": {"x": 0, "y": -9.81, "z": 0},
    "collision_enabled": true
  },
  "interaction_systems": [
    {"type": "click", "response": "select"},
    {"type": "proximity", "response": "highlight"}
  ],
  "gameplay_mechanics": {
    "type": "exploration",
    "objectives": []
  },
  "dynamic_elements": [],
  "audio_systems": {},
  "spawn_systems": {}
}
```

### 3. Technical Director

**Role**: Translates creative concepts into technical specifications.

**Responsibilities**:
- Define entity hierarchy
- Specify asset requirements
- Set performance budgets
- Plan LOD strategy
- Document platform-specific considerations
- Identify shader requirements

**Output**:
```json
{
  "entity_hierarchy": {
    "root": "World",
    "children": ["Environment", "Entities", "Lights", "Systems"]
  },
  "asset_requirements": {
    "models": [],
    "textures": [],
    "materials": []
  },
  "performance_budget": {
    "target_fps": 60,
    "max_poly_count": 500000,
    "max_texture_memory_mb": 512
  },
  "platform_considerations": {
    "unity": {"render_pipeline": "URP"},
    "unreal": {"render_pipeline": "forward"},
    "horizon": {"optimization_level": "mobile"}
  }
}
```

### 4. WDL Generator

**Role**: Synthesizes all agent outputs into a valid WDL world definition.

**Responsibilities**:
- Create WDL world structure
- Generate entity definitions
- Configure materials and lighting
- Set up interactive systems
- Ensure schema compliance

**Output**: Complete `WDLWorld` object

### 5. QA Agent

**Role**: Validates the generated world and ensures quality.

**Responsibilities**:
- Run structural validation
- Check completeness against user request
- Verify consistency across components
- Assess performance concerns
- Suggest improvements
- Approve or request revision

**Output**:
```json
{
  "completeness": "World meets user requirements",
  "consistency": "All elements are aligned",
  "performance": "Within acceptable limits",
  "improvements": ["Add more vegetation variety"],
  "issues": [],
  "approval": true,
  "score": 85
}
```

## Orchestration Flow

### State Machine

The orchestrator uses LangGraph to manage the agent workflow:

```python
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("vision", vision_agent)
workflow.add_node("systems", systems_agent)
workflow.add_node("technical", technical_agent)
workflow.add_node("wdl_generator", wdl_agent)
workflow.add_node("qa", qa_agent)

# Define edges
workflow.set_entry_point("vision")
workflow.add_edge("vision", "systems")
workflow.add_edge("systems", "technical")
workflow.add_edge("technical", "wdl_generator")
workflow.add_edge("wdl_generator", "qa")

# Conditional routing from QA
workflow.add_conditional_edges(
    "qa",
    should_continue,
    {
        "continue": "vision",  # Loop for revision
        "end": END,
    },
)
```

### Agent State

All agents share a common state object:

```python
class AgentState(BaseModel):
    user_prompt: str                    # Original user request
    vision_output: dict                 # Vision Architect output
    systems_output: dict                # Systems Designer output
    technical_output: dict              # Technical Director output
    wdl_output: dict                    # WDL Generator output
    qa_output: dict                     # QA Agent output
    messages: list[BaseMessage]         # Conversation history
    current_stage: str                  # Current pipeline stage
    iteration_count: int                # Revision iteration count
    max_iterations: int                 # Maximum allowed iterations
    errors: list[str]                   # Error messages
    is_complete: bool                   # Completion flag
```

### Revision Loop

If the QA Agent finds issues:
1. It sets `is_complete = False`
2. The workflow routes back to the Vision Architect
3. Agents can access previous outputs and QA feedback
4. Process repeats until approved or max iterations reached

## Usage

### Basic Usage

```python
from omniworld_builder.agents import WorldBuilderOrchestrator

orchestrator = WorldBuilderOrchestrator()

# Build a world from natural language
world = await orchestrator.build_world(
    "A mystical floating island with ancient ruins and magical crystals"
)

# Access the generated WDL world
print(world.to_json())
```

### With Full State

```python
world, final_state = await orchestrator.build_world_with_state(
    "A cyberpunk city at night with neon lights",
    max_iterations=3
)

# Access all agent outputs
print(final_state.vision_output)
print(final_state.systems_output)
print(final_state.technical_output)
print(final_state.qa_output)
```

### Custom Model

```python
orchestrator = WorldBuilderOrchestrator(
    model_name="claude-sonnet-4-20250514"
)
```

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: API key for Claude models

### Model Selection

The system uses Anthropic's Claude models by default. You can specify different models:

```python
orchestrator = WorldBuilderOrchestrator(model_name="claude-sonnet-4-20250514")
```

## Extending the System

### Adding Custom Agents

1. Create a new agent class extending `BaseAgent`
2. Implement `get_system_prompt()` and `process()`
3. Add the agent node to the orchestrator graph

### Custom Validation Rules

```python
from omniworld_builder.core import WDLValidator

validator = WDLValidator()

def custom_rule(world):
    issues = []
    # Your validation logic
    return issues

validator.add_rule(custom_rule)
```
