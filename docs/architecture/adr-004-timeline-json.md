# ADR-004: Timeline Engine as JSON State

## Status

Accepted

## Context

Traditional video editors store timeline state in proprietary binary formats or complex object graphs. This creates challenges for:

1. **AI Integration**: AI systems need structured, manipulable representations
2. **Undo/Redo**: Complex state management for professional editing operations
3. **Collaboration**: Difficult to merge changes or support real-time collaboration
4. **Plugin System**: Plugins need safe, validated access to timeline data
5. **Serialization**: Saving/loading projects must be reliable and versioned
6. **Preview Generation**: Need efficient way to render timeline state without full renders

Modern tools (Figma, Notion) use JSON-based state management with great success for collaborative features and extensibility.

## Decision

VID-ED implements a **JSON-Native Timeline Engine**:

### Core Principles

1. **Timeline as Immutable Snapshots**: Each edit creates a new timeline state
2. **JSON Schema Validation**: All timeline modifications must conform to schema
3. **Declarative Representation**: Timeline describes "what" not "how"
4. **Delta-Based Operations**: Edits are represented as patches, not full replacements
5. **Agent-Compatible**: AI agents produce JSON patches, not direct mutations

### Timeline JSON Schema (Simplified)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "version": { "type": "string" },
    "id": { "type": "string", "format": "uuid" },
    "name": { "type": "string" },
    "settings": {
      "type": "object",
      "properties": {
        "resolution": { "$ref": "#/definitions/resolution" },
        "frameRate": { "type": "number" },
        "duration": { "type": "number" },
        "aspectRatio": { "type": "string" }
      }
    },
    "tracks": {
      "type": "array",
      "items": { "$ref": "#/definitions/track" }
    },
    "markers": {
      "type": "array",
      "items": { "$ref": "#/definitions/marker" }
    },
    "transitions": {
      "type": "array",
      "items": { "$ref": "#/definitions/transition" }
    },
    "effects": {
      "type": "array",
      "items": { "$ref": "#/definitions/effect" }
    }
  },
  "definitions": {
    "track": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "type": { "enum": ["video", "audio", "text", "graphics"] },
        "name": { "type": "string" },
        "clips": {
          "type": "array",
          "items": { "$ref": "#/definitions/clip" }
        },
        "locked": { "type": "boolean" },
        "muted": { "type": "boolean" },
        "opacity": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "clip": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "sourceId": { "type": "string" },
        "start": { "type": "number" },
        "end": { "type": "number" },
        "inPoint": { "type": "number" },
        "outPoint": { "type": "number" },
        "offset": { "type": "number" },
        "speed": { "type": "number", "minimum": 0 },
        "keyframes": {
          "type": "array",
          "items": { "$ref": "#/definitions/keyframe" }
        }
      }
    }
  }
}
```

### Edit Operations as JSON Patches

Instead of mutating the timeline directly, all edits are expressed as RFC 6902 JSON patches:

```json
{
  "operation_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "agent": "creative_director",
  "patches": [
    {
      "op": "add",
      "path": "/tracks/0/clips/-",
      "value": {
        "id": "clip_123",
        "sourceId": "media_456",
        "start": 0,
        "end": 5.5,
        "inPoint": 10.0,
        "outPoint": 15.5,
        "offset": 0
      }
    },
    {
      "op": "replace",
      "path": "/tracks/0/clips/0/speed",
      "value": 1.5
    }
  ]
}
```

### Operation Types

| Operation | Description | Example |
|-----------|-------------|---------|
| `add_clip` | Insert clip at position | Add B-roll to track 2 |
| `remove_clip` | Delete clip from timeline | Remove unwanted segment |
| `trim_clip` | Adjust in/out points | Tighten pacing |
| `split_clip` | Cut clip into two | Create separation point |
| `merge_clips` | Join adjacent clips | Remove gap |
| `move_clip` | Change clip position | Rearrange sequence |
| `adjust_speed` | Change playback speed | Slow motion effect |
| `add_transition` | Insert transition between clips | Cross dissolve |
| `add_effect` | Apply effect to clip | Color correction |
| `add_keyframe` | Animate property over time | Opacity fade |
| `ripple_delete` | Delete and close gap | Remove section |
| `slip_edit` | Shift content without changing duration | Adjust timing |
| `slide_edit` | Move clip with adjacent clips | Preserve sync |

### Undo/Redo Architecture

```rust
pub struct TimelineHistory {
    states: Vec<TimelineState>,
    current_index: usize,
    max_history: usize,
}

impl TimelineHistory {
    pub fn push(&mut self, state: TimelineState) {
        // Truncate future states if we're not at the end
        self.states.truncate(self.current_index + 1);
        
        // Add new state
        self.states.push(state);
        self.current_index = self.states.len() - 1;
        
        // Enforce max history limit
        if self.states.len() > self.max_history {
            self.states.remove(0);
        }
    }
    
    pub fn undo(&mut self) -> Option<&TimelineState> {
        if self.current_index > 0 {
            self.current_index -= 1;
            Some(&self.states[self.current_index])
        } else {
            None
        }
    }
    
    pub fn redo(&mut self) -> Option<&TimelineState> {
        if self.current_index < self.states.len() - 1 {
            self.current_index += 1;
            Some(&self.states[self.current_index])
        } else {
            None
        }
    }
}
```

### Preview Pipeline

```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│ Timeline JSON│ →   │ Plan Builder│ →   │ Render Graph │
└──────────────┘     └─────────────┘     └──────────────┘
                            ↓                    ↓
                   ┌─────────────┐     ┌──────────────┐
                   │ Dependency  │     │ FFmpeg/OpenCV│
                   │ Resolution  │     │ Execution    │
                   └─────────────┘     └──────────────┘
                                              ↓
                                     ┌─────────────┐
                                     │  Preview    │
                                     │  Frame      │
                                     └─────────────┘
```

## Consequences

### Positive

- **AI-Friendly**: LLMs naturally produce and manipulate JSON
- **Version Control**: Timeline diffs are human-readable
- **Validation**: Schema enforcement prevents invalid states
- **Extensibility**: New operation types don't break existing code
- **Debugging**: Easy to log, inspect, and replay timeline states
- **Collaboration**: Foundation for future real-time sync (CRDTs)
- **Plugin Safety**: Plugins can only make validated changes

### Negative

- **Performance Overhead**: JSON parsing/serialization adds latency
- **Memory Usage**: Storing multiple timeline snapshots consumes RAM
- **Complexity**: More abstraction layers than direct manipulation
- **Validation Cost**: Schema validation on every edit

### Mitigation Strategies

- Use binary JSON format (BSON/MessagePack) for internal storage
- Implement lazy loading for timeline segments outside viewport
- Compress historical states beyond undo stack depth
- Cache validated timeline segments
- Use incremental validation (only validate changed portions)
- Implement memory-mapped files for large projects

## Implementation Details

### Rust Timeline Engine Structure

```rust
// src-tauri/src/timeline/mod.rs

pub mod engine;
pub mod operations;
pub mod schema;
pub mod history;
pub mod preview;

// Core types
pub struct Timeline {
    pub id: Uuid,
    pub name: String,
    pub settings: TimelineSettings,
    pub tracks: Vec<Track>,
    pub markers: Vec<Marker>,
    version: u64,
}

pub trait TimelineOperation: Send + Sync {
    fn apply(&self, timeline: &mut Timeline) -> Result<(), TimelineError>;
    fn rollback(&self, timeline: &mut Timeline) -> Result<(), TimelineError>;
    fn validate(&self, timeline: &Timeline) -> Result<(), ValidationError>;
    fn to_patch(&self) -> JsonPatch;
}
```

### File Format

Project files use `.ved` extension (ZIP-compressed JSON):

```
project.ved
├── timeline.json      # Main timeline state
├── media.json         # Media library references
├── thumbnails/        # Generated thumbnails
│   ├── thumb_001.jpg
│   └── ...
├── cache/             # Render cache
│   └── preview_frames/
└── metadata.json      # Project metadata
```

## References

- [RFC 6902: JSON Patch](https://datatracker.ietf.org/doc/html/rfc6902)
- [JSON Schema Specification](https://json-schema.org/)
- Figma's CRDT implementation analysis
- Adobe Premiere Pro project file structure research
- DaVinci Resolve database architecture
- Operational Transform vs CRDT comparison studies
