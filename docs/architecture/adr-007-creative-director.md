# ADR-007: Single Creative Director Interface

## Status

Accepted

## Context

AI video editing systems face a critical UX challenge: how to provide powerful AI capabilities without overwhelming users with complexity.

Current approaches in the market:

1. **Feature Dashboard**: Expose every AI capability as a separate button/tool
   - Problem: Cognitive overload, difficult to discover right tool
   
2. **Chat-Only**: Pure conversational interface
   - Problem: Inefficient for precise editing tasks, hard to reference timeline elements
   
3. **Hybrid Confusion**: Mix of chat and buttons with unclear boundaries
   - Problem: Users don't know when to use which interface

Professional editors need both conversational guidance AND precise control.

## Decision

VID-ED implements a **Single Creative Director Interface** with layered interaction:

### Core Principle

**The user interacts with ONE AI persona: the Creative Director**

All specialized agents (Caption, Motion, Audio, Color, etc.) are implementation details never exposed in the UI.

### Interface Architecture

```
┌─────────────────────────────────────────────────────┐
│                    WORKSPACE                        │
│                                                     │
│  ┌─────────────────────────────────────────────┐    │
│  │              PREVIEW PANEL                   │    │
│  │                                              │    │
│  │          [Video Preview Render]              │    │
│  │                                              │    │
│  └─────────────────────────────────────────────┘    │
│                                                     │
│  ┌──────────────────┐  ┌──────────────────────────┐ │
│  │   MEDIA LIBRARY  │  │      TIMELINE            │ │
│  │                  │  │                          │ │
│  │  [Media Items]   │  │  [Track 1] ████████████  │ │
│  │                  │  │  [Track 2] ████░░██████  │ │
│  │                  │  │  [Track 3] ▓▓▓▓▓▓▓▓▓▓▓▓  │ │
│  └──────────────────┘  └──────────────────────────┘ │
│                                                     │
│  ┌─────────────────────────────────────────────────┐│
│  │        CREATIVE DIRECTOR (Always Visible)       ││
│  │  ┌───────────────────────────────────────────┐  ││
│  │  │ 💬 How can I help you today?              │  ││
│  │  │                                           │  ││
│  │  │ [Type your request...]             [Send] │  ││
│  │  └───────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

### Interaction Modes

The Creative Director supports multiple interaction patterns:

#### 1. Natural Language Requests

```
User: "Make this intro more dynamic"
Creative Director: "I'll add quick cuts, zoom effects, and upbeat music. 
                    Here's what I'm planning... [shows preview]
                    Should I apply these changes?"
```

#### 2. Timeline Selection + Command

```
User: [Selects clip range 0:05-0:15]
User: "Add captions here"
Creative Director: "Generating captions for selected segment...
                    Done! Review the timing and style."
```

#### 3. Visual Reference

```
User: [Uploads reference video]
User: "Match this editing style"
Creative Director: "Analyzing reference...
                    Detected: Fast cuts (avg 2.3s), jump cuts, 
                    bold captions, color grade: teal/orange
                    Apply this style to your project?"
```

#### 4. Iterative Refinement

```
Creative Director: "Here's the first draft"
User: "Too fast, slow down the pacing"
Creative Director: "Adjusting... extended clip durations by 30%,
                    removed 3 transitions. Better?"
```

### Creative Director Personality

```
System Prompt Guidelines:

ROLE: You are the Creative Director for VID-ED

PERSONALITY TRAITS:
- Professional but approachable
- Concise but thorough  
- Proactive in suggesting improvements
- Patient with revisions
- Knowledgeable about video production

COMMUNICATION STYLE:
- Use video editing terminology correctly
- Explain technical decisions briefly
- Always confirm before making major changes
- Show progress during long operations
- Present alternatives when requests are ambiguous

CONSTRAINTS:
- NEVER mention internal agents (Caption Agent, Motion Agent, etc.)
- NEVER say "I'll delegate this to..." or "Let me ask the..."
- ALWAYS present as a single unified assistant
- Prioritize local processing for privacy
- Be honest about limitations

EXAMPLE RESPONSES:

Good: "I'll enhance the audio by reducing background noise and 
       balancing levels. This will take about 30 seconds."

Bad: "I'm sending this to the Audio Agent for processing."

Good: "I noticed the color looks inconsistent between shots. 
       Want me to match them?"

Bad: "The Color Agent detected an issue."
```

### Response Structure

All Creative Director responses follow this structure:

```json
{
  "message": {
    "text": "Human-readable response",
    "attachments": [
      {
        "type": "timeline_preview",
        "data": { /* timeline JSON snippet */ }
      },
      {
        "type": "comparison_slider",
        "before": "frame_before.jpg",
        "after": "frame_after.jpg"
      }
    ]
  },
  "actions": [
    {
      "label": "Apply Changes",
      "action": "apply_timeline_patch",
      "payload": { /* patch data */ }
    },
    {
      "label": "Try Different Style",
      "action": "regenerate_with_options",
      "payload": { /* options */ }
    },
    {
      "label": "Undo",
      "action": "undo_last_change",
      "payload": {}
    }
  ],
  "status": "awaiting_approval",
  "estimated_duration_ms": 5000
}
```

### State Management

```rust
pub struct CreativeDirectorState {
    conversation_history: Vec<Message>,
    current_task: Option<ActiveTask>,
    pending_changes: Option<TimelinePatch>,
    context: EditorContext,
}

pub struct EditorContext {
    timeline_state: Timeline,
    selected_clips: Vec<ClipId>,
    playhead_position: Duration,
    active_tracks: Vec<TrackId>,
    recent_operations: Vec<Operation>,
}

impl CreativeDirector {
    pub async fn process_request(
        &mut self,
        request: UserRequest,
        context: EditorContext,
    ) -> Result<CreativeDirectorResponse, Error> {
        // Enrich request with context
        let enriched = self.enrich_with_context(request, &context);
        
        // Generate response using LLM
        let response = self.llm.generate(enriched).await?;
        
        // Parse into structured response
        let parsed = self.parse_response(response)?;
        
        // Validate any proposed changes
        if let Some(patch) = &parsed.proposed_patch {
            self.validate_patch(patch, &context.timeline_state)?;
        }
        
        Ok(parsed)
    }
}
```

### Approval Workflow

Critical design decision: **AI never auto-applies major changes**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │ →   │  Creative   │ →   │  Internal   │
│   Request   │     │  Director   │     │  Processing │
└─────────────┘     └─────────────┘     └─────────────┘
                                               ↓
                                    ┌─────────────────────┐
                                    │ Generate Proposal   │
                                    │ (Timeline Patch)    │
                                    └─────────────────────┘
                                               ↓
                                    ┌─────────────────────┐
                                    │ Show Preview +      │
                                    │ Ask for Approval    │
                                    └─────────────────────┘
                                               ↓
                              ┌────────────────┴────────────────┐
                              ↓                                  ↓
                     ┌─────────────┐                    ┌─────────────┐
                     │   Approved  │                    │   Rejected  │
                     └──────┬──────┘                    └──────┬──────┘
                            ↓                                   ↓
                   ┌─────────────────┐                 ┌─────────────┐
                   │ Apply Changes   │                 │ Offer       │
                   │ Show Success    │                 │ Alternatives│
                   └─────────────────┘                 └─────────────┘
```

### Exception: Auto-Apply for Minor Operations

Some operations can be auto-applied with implicit approval:

| Operation | Auto-Apply | Rationale |
|-----------|------------|-----------|
| Caption generation | ✅ Yes | Non-destructive, easily reversible |
| Silence removal | ✅ Yes | Clearly improves quality |
| Basic color correction | ✅ Yes | Subtle adjustments |
| Clip trimming (>1s) | ❌ No | Significant content change |
| Effect application | ❌ No | Dramatic visual change |
| Track deletion | ❌ No | Destructive operation |
| Export/render | ❌ No | Time-consuming, irreversible |

## Consequences

### Positive

- **Simplicity**: One interface to learn, one AI to trust
- **Consistency**: Unified personality across all features
- **Flexibility**: New capabilities don't require UI changes
- **Discoverability**: Users can ask rather than search for features
- **Professional Feel**: Matches how real creative directors work
- **Reduced Anxiety**: Approval workflow prevents unwanted changes

### Negative

- **Abstraction Layer**: Extra processing between intent and execution
- **LLM Dependency**: Quality depends on language model capabilities
- **Latency**: Multi-step processing may feel slower than direct tools
- **Ambiguity Handling**: Natural language can be imprecise
- **Power User Friction**: Experts may prefer direct manipulation

### Mitigation Strategies

- Implement streaming responses to show progress
- Add keyboard shortcuts for common commands
- Allow power users to enable "quick apply" mode
- Provide visual timeline scrubbing alongside chat
- Cache common responses for instant replies
- Support command palette for direct access to features

## References

- Figma's AI interface patterns
- Adobe Firefly integration studies
- Cursor IDE conversational UX analysis
- Linear's keyboard-first design philosophy
- Conversational AI best practices (Google, Microsoft)
- Professional editor workflow research
