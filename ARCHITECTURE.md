# VID-ED Architecture

**VID-ED** is a Windows-native AI Creative Operating System combining desktop-class performance with local AI inference.

## System Composition

```
┌─────────────────────────────────────────────────────────┐
│                   TAURI DESKTOP SHELL                   │
│                    (src-tauri/src/main.rs)              │
│                                                         │
│  - Window management                                    │
│  - Native OS integration                                │
│  - IPC routing                                          │
│  - Plugin lifecycle                                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                    IPC Bridge
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
     RUST CORE    REACT UI    PYTHON AI RUNTIME
   (src-tauri)  (src/renderer) (ai-runtime)
```

### Tier 1: Desktop Shell (Tauri v2)

- **Framework**: Tauri 2.x
- **Location**: `src-tauri/`
- **Responsibility**:
  - Window lifecycle management
  - Native OS APIs (file dialogs, system notifications, clipboard)
  - IPC message routing
  - Plugin system orchestration
  - Main menu and shortcuts
  - Tray integration

**Key File**:
- `src-tauri/src/main.rs` — Tauri app entry point
- `src-tauri/Cargo.toml` — Rust dependencies

### Tier 2: Rust Core

- **Location**: `src-tauri/src/`
- **Modules**:
  - `timeline/` — Shared timeline engine
  - `renderer/` — FFmpeg coordination, render graph
  - `plugin/` — Plugin SDK, sandboxing, lifecycle
  - `ai/` — IPC bridge to Python runtime
  - `hardware/` — Hardware detection, adaptation
  - `event/` — Event bus for all components
  - `security/` — Access control, audit logging

**Responsibility**:
- Core business logic (timeline operations, rendering)
- Plugin system and permissions
- IPC protocol and validation
- Async task scheduling

### Tier 3: React Frontend

- **Location**: `src/renderer/`
- **Framework**: React 18+, TypeScript
- **Build**: Vite
- **Styling**: Tailwind CSS + Luminous Editorial tokens
- **State**: Redux or Zustand
- **Key Packages**:
  - `src/renderer/src/shared/` — Shared TypeScript types
  - `src/renderer/src/components/` — Reusable React components
  - `src/renderer/src/pages/` — Feature pages (editor, library, settings)
  - `src/renderer/src/hooks/` — Custom React hooks for IPC, state, etc.

**Responsibility**:
- User interface rendering
- Event handling and user interactions
- Component lifecycle
- State synchronization with Rust core
- Design system implementation (Luminous Editorial)

### Tier 4: Python AI Runtime

- **Location**: `ai-runtime/`
- **Framework**: FastAPI (internal service only)
- **Server**: uvicorn (localhost:8000)
- **Key Modules**:
  - `core/` — LLM client, job queue, security manager
  - `schemas/` — Pydantic validation models
  - `agents/` — Specialized editing agents
  - `inference/` — Model routing and selection
  - `memory/` — Local RAG, embeddings
  - `vision/` — CV pipelines (YOLO, MediaPipe, Whisper)
  - `orchestrator/` — Agent coordination

**Responsibility**:
- AI inference (local models only by default)
- Background task execution
- Model lifecycle management
- Knowledge base and memory systems
- Computer vision pipelines

**Security Constraints**:
- ✅ Listens ONLY on `127.0.0.1:8000`
- ✅ No external network access (unless user explicitly enables cloud features)
- ✅ Request/response validation via Pydantic
- ✅ Sandboxed file access (permitted directories only)
- ✅ Automatic timeout and cancellation

---

## Communication Protocols

### IPC (Rust ↔ React)

**Mechanism**: Tauri IPC commands

**Example Flow**:
```typescript
// React: Trigger timeline export
const response = await invoke('export_timeline', { timeline, settings });

// Rust: Handle the command
#[tauri::command]
pub async fn export_timeline(timeline: TimelineData, settings: ExportSettings) -> Result<String> {
    // Coordinate with Python runtime, call FFmpeg
}
```

**Guarantee**: Strongly typed, validated on both sides.

### HTTP (Rust ↔ Python)

**Mechanism**: HTTP over localhost

**Example Flow**:
```rust
// Rust: Request caption generation
let response = client.post("http://127.0.0.1:8000/agents/caption/generate")
    .json(&CaptionRequest { ... })
    .send()
    .await?;

// Python: Validate and execute
@router.post("/agents/caption/generate")
async def generate_captions(request: CaptionRequest) -> CaptionResponse:
    # Validate, execute, return
```

**Guarantee**: HTTP 200/400/500, JSON response validated against Pydantic schema.

---

## Data Flows

### 1. User Edits Timeline

```
React Component
    ↓
emit('timeline/update')
    ↓
Tauri IPC Command
    ↓
Rust Core (Timeline Engine)
    ↓
Broadcast Event
    ↓
[React] Update UI state
[Python] Trigger smart agent
    ↓
HTTP Request to Python
    ↓
Model Inference
    ↓
HTTP Response with suggestions
    ↓
Rust Core queues render
    ↓
FFmpeg renders
```

### 2. User Requests AI Suggestion

```
React: "Suggest captions"
    ↓
Tauri IPC: request_caption_suggestions(timeline)
    ↓
Rust Core validates timeline
    ↓
HTTP POST → Python: /agents/caption/generate
    ↓
Python validates request
    ↓
LLM Router selects model
    ↓
Load model (if needed)
    ↓
Execute inference
    ↓
Return suggestions
    ↓
Rust Core queues for validation
    ↓
React receives via IPC
    ↓
Display suggestions to user
```

### 3. Export Video

```
React: "Export to H.264"
    ↓
Tauri IPC: export_video(timeline, format, quality)
    ↓
Rust Core validates timeline
    ↓
Rust Core: generate render plan
    ↓
Rust Core: coordinate FFmpeg (local rendering)
    ↓
If preview: stream to React
If final: save to disk
    ↓
Python: perform quality checks (optional)
    ↓
React: notify user
```

---

## Data Storage

### Config Files

- `~/.config/vid-ed/` (Windows: `%APPDATA%/vid-ed/`)
  - `config.json` — User preferences, hardware profile
  - `projects/` — Project metadata
  - `cache/` — Model cache, embeddings

### Project Structure

```
~/Projects/MyShot/
├── project.json           # Timeline + metadata
├── .vid-ed/
│   ├── cache.db          # SQLite: video analysis cache
│   ├── thumbnails/       # Cached thumbnails
│   ├── renders/          # Intermediate renders
│   └── memory.db         # Agent memory, knowledge base
├── media/
│   ├── source/           # Input videos/images
│   ├── music/            # Audio tracks
│   └── assets/           # Brand assets, b-roll
└── exports/              # Final outputs
```

### Databases

**SQLite**: Lightweight, offline-first
- `project.db` — Timeline structure, effects, metadata
- `cache.db` — Video analysis results (scene detection, faces, OCR, etc.)
- `memory.db` — Creator profile, brand rules, embeddings

**Optional ChromaDB**: Local vector database (if enabled)
- Semantic search over projects, research, notes

---

## Dependency Management

### Rust Workspace

**Location**: `src-tauri/Cargo.toml`

```toml
[workspace]
members = ["src-tauri", "src-tauri/crates/timeline", "src-tauri/crates/plugins"]
resolver = "2"
```

**Key Crates**:
- `tauri` — Desktop framework
- `tokio` — Async runtime
- `serde` — Serialization
- `rusqlite` — SQLite
- `reqwest` — HTTP client
- `chrono` — Time handling

### Node.js Workspace

**Location**: `package.json`

```json
{
  "workspaces": ["src/renderer"]
}
```

**Key Dependencies**:
- `react` — UI framework
- `react-dom` — DOM rendering
- `typescript` — Type safety
- `vite` — Build tool
- `tailwindcss` — Styling
- `@tauri-apps/api` — Tauri IPC client

### Python Virtual Environment

**Location**: `ai-runtime/`

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate.bat  # Windows
```

**Dependencies**: `requirements.txt`
- `fastapi` — Web framework
- `uvicorn` — ASGI server
- `pydantic` — Validation
- `ollama` — Local LLM client
- `opencv-python` — Computer vision
- `torch` — Deep learning (optional, for local inference)

---

## Build & Deployment

### Development

```bash
# Terminal 1: Python AI runtime
cd ai-runtime
python -m pip install -r requirements.txt
python -m vid_ed_ai.main

# Terminal 2: React frontend (dev server)
cd src/renderer
npm install
npm run dev

# Terminal 3: Tauri app
cd src-tauri
cargo tauri dev
```

### Production Build

```bash
# Build Python runtime (freeze dependencies)
cd ai-runtime
pip install -r requirements.txt
# Bundle into binary (e.g., PyInstaller)

# Build React (static assets)
cd src/renderer
npm run build

# Build Tauri (Windows MSI installer)
cd src-tauri
cargo tauri build --target x86_64-pc-windows-msvc
```

**Output**: `src-tauri/target/release/bundle/msi/Aether-Studio-*.msi`

---

## Testing Strategy

### Unit Tests

- **Rust**: `cargo test` in `src-tauri/`
- **React**: Jest/Vitest in `src/renderer/`
- **Python**: pytest in `ai-runtime/`

### Integration Tests

- **Tauri IPC**: Verify Rust ↔ React commands
- **HTTP API**: Verify Rust ↔ Python communication
- **Timeline Engine**: Create, edit, render cycles

### E2E Tests

- **Playwright**: Full user flows (import, edit, export)
- **Performance**: Benchmark render times, memory usage

---

## Offline Capability

**Guarantee**: VID-ED works completely offline by default.

- ✅ No internet required to start
- ✅ No telemetry or analytics (optional opt-in)
- ✅ No cloud model dependency
- ✅ Local LLMs via Ollama
- ✅ Local embeddings via ChromaDB or Chroma
- ✅ Offline project storage in SQLite
- ⚠️ Cloud features (B-roll generation, AI voice) optional only

---

## Security Model

### Sandboxing

**Plugins**: Run in restricted environment with explicit capabilities.

**Python Runtime**: Restricted to `localhost:127.0.0.1`, sandboxed file access.

**FFmpeg**: Argument validation, no arbitrary command execution.

### Permissions

Every operation (file access, model loading, render execution) validated against:
- User intent
- Plugin capabilities
- Resource limits
- Audit log

### Encryption

- Project data: Optional AES-256 (user's local machine only)
- No credentials stored in plaintext
- API keys encrypted and isolated

---

## Observability

**Structured Logging**:
```json
{
  "timestamp": "2026-07-14T12:00:00Z",
  "level": "INFO",
  "module": "timeline.renderer",
  "event": "render_started",
  "timeline_id": "abc123",
  "frame_count": 1200,
  "target_fps": 30
}
```

**Metrics**:
- Memory usage (RAM, VRAM)
- CPU utilization
- Model load times
- Render performance
- IPC latency

**Crash Reporting**: Local collection (optional cloud upload with user consent)

---

## Performance Targets

| Operation | Target | Hardware |
|-----------|--------|----------|
| Open project | < 500ms | 8GB RAM |
| Create caption | < 2s | 8GB RAM, 0.5B model |
| Preview render (30s clip, 1080p) | < 5s | 16GB RAM |
| Export H.264 (30s clip, 1080p) | < 30s | 16GB RAM |
| Plugin load | < 100ms | Any |
| IPC command roundtrip | < 50ms | Any |

---

## Versioning & Compatibility

### Semantic Versioning

- **MAJOR**: Breaking changes (plugin API, timeline format)
- **MINOR**: New features (agents, AI models)
- **PATCH**: Bug fixes, performance improvements

### Project File Format

Timeline stored as versioned JSON. Migration scripts support loading older projects.

### Plugin SDK

Plugin API versioned independently. Backwards compatibility guaranteed within major version.

---

## Next Steps

1. **Implement Tauri Shell**: Window creation, menu, IPC routing
2. **Build Rust Core**: Timeline engine, plugin system
3. **Create React UI**: Design system integration, component library
4. **Integrate Python Runtime**: LLM client, job queue, agent coordination
5. **End-to-End Testing**: Verify all layers communicate correctly
6. **Documentation**: ADRs, API docs, architecture decision record

---

**Maintained by**: VID-ED Architecture Team  
**Last Updated**: 2026-07-14  
**Status**: Active Development
