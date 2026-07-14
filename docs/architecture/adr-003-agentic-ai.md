# ADR-003: Agentic AI System Design

## Status

Accepted

## Context

AI-powered video editing requires multiple specialized capabilities:
- Understanding video content (scenes, objects, motion)
- Processing audio (speech recognition, enhancement, music)
- Generating edits (cuts, transitions, effects)
- Writing captions and scripts
- Researching trends and competitors
- Managing brand consistency

A naive approach would expose each capability as a separate tool or button, creating:
- Cognitive overload for users
- Complex UI with dozens of features
- Fragmented workflows
- Inconsistent AI behavior

Professional editors expect a unified, intuitive interface—not a dashboard of AI tools.

## Decision

VID-ED implements a **Multi-Agent System with Single Interface**:

### Architecture

```
┌─────────────────────────────────────────────┐
│              USER INTERFACE                 │
│                                             │
│        ┌─────────────────────┐              │
│        │  Creative Director  │ ← ONLY visible AI
│        │      (Chat UI)      │              │
│        └─────────────────────┘              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           ORCHESTRATION LAYER               │
│                                             │
│  ┌──────────────┐    ┌──────────────┐       │
│  │ Task Planner │ →  │  Scheduler   │       │
│  └──────────────┘    └──────────────┘       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          SPECIALIZED AGENTS LAYER           │
│                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ Story   │ │ Caption │ │ Motion  │ ...    │
│  │ Agent   │ │ Agent   │ │ Agent   │        │
│  └─────────┘ └─────────┘ └─────────┘        │
│                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ Audio   │ │ Color   │ │  VFX    │        │
│  │ Agent   │ │ Agent   │ │ Agent   │        │
│  └─────────┘ └─────────┘ └─────────┘        │
│                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │Research │ │ Brand   │ │ Publish │        │
│  │ Agent   │ │ Agent   │ │ Agent   │        │
│  └─────────┘ └─────────┘ └─────────┘        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           TIMELINE ENGINE                   │
│        (JSON State Representation)          │
└─────────────────────────────────────────────┘
```

### Key Principles

1. **Single AI Persona**: Users interact only with the "Creative Director"
2. **Agent Abstraction**: Specialized agents are implementation details, never exposed
3. **Delegation Pattern**: Creative Director delegates tasks to appropriate agents
4. **Unified Output**: All agents produce timeline JSON, not direct modifications
5. **Human-in-the-Loop**: User reviews and approves all AI-suggested edits

### Agent Responsibilities

| Agent | Responsibility | Local/Cloud |
|-------|---------------|-------------|
| Creative Director | User interaction, task decomposition | Local (LLM) |
| Task Planner | Break down requests into actionable steps | Local (LLM) |
| Scheduler | Prioritize and queue agent tasks | Local (Rule-based) |
| Story Agent | Narrative structure, pacing, shot selection | Local (LLM + Vision) |
| Caption Agent | Speech-to-text, caption styling, timing | Local (Whisper) |
| Motion Agent | Motion tracking, stabilization, keyframes | Local (OpenCV) |
| Audio Agent | Noise reduction, leveling, EQ | Local (ONNX) |
| Voice Agent | Voice enhancement, dubbing | Local (ONNX) |
| Color Agent | Color correction, grading suggestions | Local (ONNX + LLM) |
| VFX Agent | Visual effects, compositing | Local (FFmpeg + OpenCV) |
| Research Agent | Trend analysis, competitor research | Cloud (Optional) |
| Brand Agent | Brand consistency, style enforcement | Local (Vector DB) |
| Publishing Agent | Platform optimization, metadata | Local + Cloud (APIs) |
| Review Agent | Quality checks, error detection | Local (LLM + Rules) |
| Timeline Agent | Direct timeline manipulation | Local (Rust) |

### Communication Protocol

Agents communicate via structured JSON messages:

```json
{
  "task_id": "uuid",
  "agent": "caption_agent",
  "action": "generate_captions",
  "input": {
    "clip_id": "clip_123",
    "language": "en",
    "style": "minimal"
  },
  "output": {
    "captions": [...],
    "confidence": 0.95,
    "processing_time_ms": 1200
  },
  "status": "completed"
}
```

## Consequences

### Positive

- **Simplicity**: One chat interface instead of 20 buttons
- **Flexibility**: Agents can be added/removed without UI changes
- **Consistency**: Unified AI personality across all features
- **Scalability**: New capabilities don't increase UI complexity
- **Trust**: Users build relationship with one AI assistant
- **Debugging**: Clear separation of concerns for troubleshooting

### Negative

- **Abstraction Overhead**: Extra layer between user intent and execution
- **Agent Coordination**: Complex orchestration logic required
- **Error Propagation**: Failures in one agent can cascade
- **Latency**: Multiple agent handoffs may slow responses
- **Testing Complexity**: Must test individual agents and orchestration

### Mitigation Strategies

- Implement robust task queuing with priority levels
- Add timeout and retry logic for agent failures
- Build comprehensive logging and tracing across agents
- Create agent simulation mocks for testing orchestration
- Use streaming responses to show progress during multi-agent tasks
- Implement circuit breakers to prevent cascade failures

## Implementation Details

### Creative Director Prompt Structure

```
You are the Creative Director for VID-ED, a professional AI video editing system.

Your role:
1. Understand the user's creative vision
2. Break down complex requests into specific tasks
3. Delegate to specialized agents
4. Present results clearly to the user
5. Iterate based on feedback

Constraints:
- Never mention internal agents by name
- Always present yourself as a single assistant
- Prioritize user privacy (local processing)
- Be concise but thorough
- Suggest alternatives when requests are unclear

Available capabilities:
- Video editing and trimming
- Caption generation
- Color correction
- Audio enhancement
- Motion tracking
- Visual effects
- Trend research
- Brand consistency
- Multi-platform publishing
```

### Agent Registration System

Agents register with the orchestrator at startup:

```rust
pub struct AgentRegistry {
    agents: HashMap<String, Box<dyn Agent>>,
}

pub trait Agent: Send + Sync {
    fn name(&self) -> &str;
    fn capabilities(&self) -> Vec<Capability>;
    fn execute(&self, task: Task) -> Result<TaskResult, AgentError>;
    fn health_check(&self) -> HealthStatus;
}
```

## References

- [Multi-Agent Systems Research](https://www.sciencedirect.com/topics/computer-science/multi-agent-system)
- Claude's system prompt design patterns
- AutoGen framework architecture
- LangChain agent orchestration patterns
- Adobe Sensei feature analysis
- DaVinci Resolve Neural Engine documentation
