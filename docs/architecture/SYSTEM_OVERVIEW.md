# VID-ED System Architecture Overview

## Executive Summary

VID-ED is a **Local-First Agentic AI Creative Operating System** for professional video production. This document provides a high-level overview of the system architecture. Detailed design decisions are documented in individual ADRs.

## Core Principles

1. **Local-First**: All core functionality runs on the user's device
2. **Privacy by Design**: User content never leaves the device without explicit consent
3. **Single AI Interface**: Users interact only with the Creative Director
4. **JSON-Native Timeline**: All editing state is represented as validated JSON
5. **Hardware Adaptive**: Automatically optimizes for available hardware
6. **Plugin Extensible**: Secure sandboxed plugin system
7. **Offline Capable**: Full functionality without internet

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐   │
│  │   Preview   │ │   Media     │ │    Creative Director     │   │
│  │   Panel     │ │   Library   │ │    Chat Interface        │   │
│  └─────────────┘ └─────────────┘ └──────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Timeline Engine                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      TAURI APPLICATION LAYER                     │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐   │
│  │   Tauri     │ │   Rust      │ │      TypeScript          │   │
│  │   Commands  │ │   Core      │ │      Renderer            │   │
│  └─────────────┘ └─────────────┘ └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       RUST CORE SERVICES                         │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐   │
│  │   Timeline  │ │   Render    │ │      Security            │   │
│  │   Engine    │ │   Coordinator│ │     Manager             │   │
│  └─────────────┘ └─────────────┘ └──────────────────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐   │
│  │   Plugin    │ │   Memory    │ │      Hardware            │   │
│  │   Host      │ │   Manager   │ │     Detection            │   │
│  └─────────────┘ └─────────────┘ └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     AI RUNTIME (Python IPC)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐   │
│  │   Creative  │ │ Specialized │ │      Model               │   │
│  │   Director  │ │   Agents    │ │      Manager             │   │
│  └─────────────┘ └─────────────┘ └──────────────────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐   │
│  │   Research  │ │   Memory    │ │      Inference           │   │
│  │   Engine    │ │   System    │ │      Engine              │   │
│  └─────────────┘ └─────────────┘ └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    NATIVE LIBRARIES & BACKENDS                   │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐   │
│  │   FFmpeg    │ │   OpenCV    │ │      ONNX Runtime        │   │
│  └─────────────┘ └─────────────┘ └──────────────────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐   │
│  │  llama.cpp  │ │  whisper.cpp│ │      SQLite/LanceDB      │   │
│  └─────────────┘ └─────────────┘ └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Module Responsibilities

### UI Layer (React + TypeScript)
- Preview panel with real-time rendering
- Media library with AI-powered organization
- Timeline visualization and interaction
- Creative Director chat interface
- Settings and configuration panels

### Tauri Bridge
- IPC between renderer and Rust core
- Command validation and sanitization
- Event emission to UI
- State synchronization

### Rust Core
| Module | Responsibility |
|--------|---------------|
| Timeline Engine | JSON-based timeline state management, undo/redo |
| Render Coordinator | Preview generation, FFmpeg orchestration |
| Security Manager | Path validation, permission enforcement |
| Plugin Host | Sandbox management, IPC with plugins |
| Memory Manager | SQLite + LanceDB operations |
| Hardware Detection | System profiling, model selection |

### AI Runtime (Python)
| Component | Responsibility |
|-----------|---------------|
| Creative Director | User interaction, task decomposition |
| Specialized Agents | Caption, motion, audio, color, VFX processing |
| Model Manager | Load/unload models, hardware adaptation |
| Research Engine | Web analysis, trend detection |
| Memory System | Brand memory, creator preferences |
| Inference Engine | LLM, vision, audio model execution |

### Native Libraries
- **FFmpeg**: Video/audio encoding, decoding, filtering
- **OpenCV**: Computer vision, motion tracking
- **ONNX Runtime**: Neural network inference
- **llama.cpp**: Local LLM inference
- **whisper.cpp**: Speech recognition
- **SQLite**: Structured data storage
- **LanceDB**: Vector embeddings, semantic search

## Data Flow

### User Request Flow

```
User Input → Creative Director → Task Planner → Scheduler → Specialized Agents
                                                                          ↓
Timeline Patch ← Review Agent ← Validation ← Execution Results ← Agent Output
       ↓
Preview Generation → User Approval → Apply/Reject
```

### Rendering Pipeline

```
Timeline JSON → Plan Builder → Dependency Graph → FFmpeg Filter Graph
                                                        ↓
                                               Frame Extraction
                                                        ↓
                                               Preview Display
```

### Memory Operations

```
Media Import → Feature Extraction → Vector Embeddings → LanceDB
                                                              ↓
Project Save → Timeline State → Serialization → SQLite
                                                              ↓
Brand Memory → Style Analysis → Embeddings → Vector DB
```

## Security Boundaries

```
┌─────────────────────────────────────────┐
│         UNTRUSTED INPUT                 │
│  - User input                           │
│  - Plugin requests                      │
│  - External files                       │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         SECURITY MANAGER                │
│  - Path sanitization                    │
│  - Permission validation                │
│  - Rate limiting                        │
│  - Resource quotas                      │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         SANDBOXED EXECUTION             │
│  - Plugin subprocess isolation          │
│  - Restricted filesystem access         │
│  - Network access control               │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         CORE OPERATIONS                 │
│  - Validated operations only            │
│  - Audited actions                      │
│  - Encrypted storage                    │
└─────────────────────────────────────────┘
```

## Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| App Launch | < 2s | Cold start |
| Timeline Scrubbing | < 50ms | Per frame |
| AI Response | < 3s | For common requests |
| Caption Generation | Real-time | During playback |
| Preview Render | < 1s | For current frame |
| Project Save | < 500ms | Incremental |
| Plugin Load | < 1s | From disk |

## Scalability Considerations

### Horizontal Scaling (Future)
- Multi-user collaboration via CRDTs
- Distributed rendering across machines
- Cloud sync for team projects

### Vertical Scaling
- Multi-GPU support for rendering
- Large project handling (100+ tracks)
- 8K+ resolution support

## Extension Points

### Plugin API
- Timeline effects and transitions
- Media importers/exporters
- AI model extensions
- UI customizations

### Model Marketplace
- Community-contributed models
- Fine-tuned style models
- Specialized detection models

### Integration APIs
- NLE interoperability (XML, AAF)
- Asset management systems
- Publishing platforms
- Analytics services

## Monitoring & Observability

- Structured logging with tracing
- Performance metrics collection
- Error reporting with context
- Usage analytics (opt-in)
- Health checks for all subsystems

## Deployment Strategy

### Development
- Hot reload for UI
- Debug builds with full symbols
- Mock services for testing

### Production
- Code-signed binaries
- Automatic updates via Tauri Updater
- Crash reporting (opt-in)
- Telemetry for performance monitoring

## Related Documents

- [ADR-001: Local-First Architecture](adr-001-local-first.md)
- [ADR-002: Tech Stack](adr-002-tech-stack.md)
- [ADR-003: Agentic AI Design](adr-003-agentic-ai.md)
- [ADR-004: Timeline JSON](adr-004-timeline-json.md)
- [ADR-005: Hardware Adaptive](adr-005-hardware-adaptive.md)
- [ADR-006: Plugin Security](adr-006-plugin-security.md)
- [ADR-007: Creative Director](adr-007-creative-director.md)
- [ADR-008: Offline-First](adr-008-offline-first.md)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01-15 | Initial architecture definition |

---

*This document is maintained by the Engineering Team. For questions or proposed changes, open an issue or submit an RFC.*
