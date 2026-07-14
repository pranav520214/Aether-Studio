# Privantrix AI OS - Agent Framework

## Overview

The Agent Framework provides a structured way to create, manage, and execute autonomous agents within the Privantrix AI OS environment.

## Agent Types

### 1. Code Analysis Agent
- Analyzes code structure
- Identifies patterns and anti-patterns
- Suggests improvements

### 2. Documentation Agent
- Generates documentation from code
- Updates existing docs
- Creates summaries

### 3. Testing Agent
- Creates test cases
- Runs test suites
- Reports coverage

### 4. Refactoring Agent
- Identifies refactoring opportunities
- Applies safe transformations
- Validates changes

## Agent Configuration

Agents are configured in `configs/agents.json`:

```json
{
  "agents": [
    {
      "id": "code-analyst",
      "name": "Code Analyst",
      "type": "analysis",
      "model": "local-model",
      "temperature": 0.3,
      "max_tokens": 4096,
      "enabled": true
    }
  ]
}
```

## Agent Lifecycle

1. **Initialization**: Agent loads configuration and connects to required services
2. **Task Assignment**: Planner assigns tasks based on agent capabilities
3. **Execution**: Agent processes task using assigned model
4. **Memory Update**: Results stored in appropriate memory tier
5. **Checkpoint**: Progress saved for recovery

## Integration Points

- **Memory Manager**: For context retrieval and storage
- **Model Router**: For optimal model selection
- **Planner**: For task assignment and tracking
- **Database**: For persistent state

## Creating Custom Agents

```python
from src.memory import MemoryManager
from src.router import ModelRouter

class CustomAgent:
    def __init__(self, agent_id: str, config: dict):
        self.id = agent_id
        self.config = config
        self.memory = MemoryManager()
        self.router = ModelRouter()
    
    async def execute(self, task: str) -> str:
        # Get context from memory
        context = self.memory.get_context()
        
        # Select appropriate model
        model = self.router.select_model(
            required_capabilities=["reasoning"]
        )
        
        # Execute task
        result = await self._process(task, context, model)
        
        # Store result
        self.memory.add_to_memory(result, MemoryType.PROJECT)
        
        return result
    
    async def _process(self, task: str, context: str, model) -> str:
        # Implementation specific to agent type
        pass
```

## Best Practices

1. Always retrieve relevant context before execution
2. Store results in appropriate memory tier
3. Handle errors gracefully with logging
4. Create checkpoints at milestones
5. Respect model context limits
