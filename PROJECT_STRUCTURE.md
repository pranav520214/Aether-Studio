# VID-ED Project Structure

This document describes the production-grade folder structure for the VID-ED AI Video Production Operating System.

## Root Level

```
vid-ed/
├── package.json              # Root package.json for workspace
├── pnpm-workspace.yaml       # PNPM workspace configuration (recommended)
├── tsconfig.base.json        # Base TypeScript configuration
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT License
├── README.md                 # Project overview
└── PROJECT_STRUCTURE.md      # This file
```

## Frontend (React + Vite)

```
src/renderer/
├── package.json              # Renderer dependencies
├── tsconfig.json             # TypeScript config for renderer
├── vite.config.ts            # Vite build configuration
├── index.html                # Entry HTML
├── src/
│   ├── main.tsx              # React entry point
│   ├── App.tsx               # Root component
│   ├── components/           # UI components
│   │   ├── timeline/         # Timeline components
│   │   ├── preview/          # Video preview components
│   │   ├── media/            # Media library components
│   │   ├── ai/               # Creative Director chat components
│   │   └── ui/               # Reusable UI primitives
│   ├── hooks/                # Custom React hooks
│   ├── layouts/              # App layouts
│   ├── store/                # Zustand state management
│   ├── theme/                # Design system tokens
│   └── utils/                # Renderer-specific utilities
```

## Shared Module

```
src/shared/
├── package.json              # Shared module package
├── tsconfig.json             # TypeScript config
├── index.ts                  # Module exports
├── types/
│   └── index.ts              # Shared TypeScript types
├── constants/
│   └── index.ts              # Application constants
└── utils/
    └── index.ts              # Shared utility functions
```

## Tauri Backend (Rust)

```
src-tauri/
├── Cargo.toml                # Rust dependencies
├── tauri.conf.json           # Tauri configuration
├── build.rs                  # Build script
├── src/
│   ├── main.rs               # Rust entry point
│   ├── lib.rs                # Library exports
│   ├── commands/             # Tauri command handlers
│   │   ├── mod.rs
│   │   ├── timeline.rs
│   │   ├── media.rs
│   │   ├── ai.rs
│   │   ├── render.rs
│   │   └── plugins.rs
│   ├── core/                 # Core business logic
│   │   ├── mod.rs
│   │   ├── app_state.rs
│   │   └── event_bus.rs
│   ├── timeline/             # Timeline engine
│   │   ├── mod.rs
│   │   ├── engine.rs
│   │   ├── operations.rs
│   │   └── schema.rs
│   ├── media/                # Media management
│   │   ├── mod.rs
│   │   ├── import.rs
│   │   ├── analyzer.rs
│   │   └── cache.rs
│   ├── ai/                   # AI integration layer
│   │   ├── mod.rs
│   │   ├── ipc.rs
│   │   ├── agent_router.rs
│   │   └── models.rs
│   ├── render/               # Rendering engine
│   │   ├── mod.rs
│   │   ├── ffmpeg.rs
│   │   ├── preview.rs
│   │   └── export.rs
│   ├── memory/               # Vector database & SQLite
│   │   ├── mod.rs
│   │   ├── brand.rs
│   │   ├── creator.rs
│   │   └── embeddings.rs
│   ├── plugins/              # Plugin system
│   │   ├── mod.rs
│   │   ├── loader.rs
│   │   ├── sandbox.rs
│   │   └── registry.rs
│   ├── security/             # Security layer
│   │   ├── mod.rs
│   │   ├── sandbox.rs
│   │   ├── permissions.rs
│   │   └── validator.rs
│   └── utils/                # Rust utilities
│       ├── mod.rs
│       ├── fs.rs
│       └── hardware.rs
└── tests/                    # Rust integration tests
    ├── timeline_tests.rs
    ├── render_tests.rs
    └── security_tests.rs
```

## AI Runtime (Python)

```
ai-runtime/
├── pyproject.toml            # Python project configuration
├── README.md                 # AI runtime documentation
├── src/
│   └── vid_ed_ai/
│       ├── __init__.py
│       ├── main.py           # FastAPI application
│       ├── config.py         # Configuration management
│       ├── agents/           # AI agents
│       │   ├── __init__.py
│       │   ├── base.py       # Base agent class
│       │   ├── creative_director.py
│       │   ├── task_planner.py
│       │   ├── scheduler.py
│       │   ├── timeline.py
│       │   ├── story.py
│       │   ├── caption.py
│       │   ├── research.py
│       │   ├── brand.py
│       │   ├── motion.py
│       │   ├── vfx.py
│       │   ├── audio.py
│       │   ├── voice.py
│       │   ├── color.py
│       │   └── review.py
│       ├── inference/        # Model inference
│       │   ├── __init__.py
│       │   ├── llama.cpp
│       │   ├── whisper.cpp
│       │   ├── onnx.py
│       │   └── router.py
│       ├── memory/           # AI memory systems
│       │   ├── __init__.py
│       │   ├── lancedb.py
│       │   ├── sqlite.py
│       │   └── manager.py
│       ├── models/           # Model management
│       │   ├── __init__.py
│       │   ├── downloader.py
│       │   ├── loader.py
│       │   └── registry.py
│       ├── research/         # Web research engine
│       │   ├── __init__.py
│       │   ├── scraper.py
│       │   ├── analyzer.py
│       │   └── brief_generator.py
│       ├── schemas/          # Pydantic models
│       │   ├── __init__.py
│       │   ├── timeline.py
│       │   ├── agents.py
│       │   └── hardware.py
│       └── utils/            # Python utilities
│           ├── __init__.py
│           ├── hardware.py
│           └── video.py
└── tests/                    # Python tests
    ├── test_agents.py
    ├── test_inference.py
    └── test_research.py
```

## Plugins SDK

```
plugins/
├── sdk/
│   ├── package.json          # SDK dependencies
│   ├── README.md             # Plugin development guide
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts          # SDK exports
│   │   ├── types.ts          # Plugin types
│   │   ├── api.ts            # Plugin API
│   │   └── cli.ts            # Plugin CLI tools
│   └── examples/
│       ├── basic-plugin/
│       └── advanced-plugin/
└── official/                 # Official plugins
    ├── color-grading/
    ├── audio-enhancement/
    └── social-export/
```

## Documentation

```
docs/
├── README.md
├── architecture/
│   ├── SYSTEM_OVERVIEW.md
│   ├── adr-001-local-first.md
│   ├── adr-002-tech-stack.md
│   ├── adr-003-agentic-ai.md
│   ├── adr-004-timeline-json.md
│   ├── adr-005-hardware-adaptive.md
│   ├── adr-006-plugin-security.md
│   ├── adr-007-creative-director.md
│   └── adr-008-offline-first.md
├── api/                      # API documentation
├── guides/                   # User guides
├── contributing/             # Contribution guidelines
└── changelog/                # Version changelogs
```

## Testing

```
tests/
├── unit/                     # Unit tests
│   ├── renderer/
│   ├── shared/
│   └── rust/
├── integration/              # Integration tests
│   ├── timeline/
│   ├── ai-ipc/
│   └── render/
└── e2e/                      # End-to-end tests
    ├── workflows/
    └── performance/
```

## Scripts

```
scripts/
├── setup.sh                  # Development environment setup
├── build.sh                  # Build all modules
├── test.sh                   # Run all tests
├── lint.sh                   # Run linters
├── release.sh                # Release automation
└── download-models.py        # AI model downloader
```

## Key Design Decisions

### 1. Monorepo Structure
- Single repository for all code
- Shared types ensure type safety across boundaries
- Easier cross-module refactoring

### 2. Clear Boundaries
- `src/shared`: Only pure, isomorphic code
- `src/renderer`: Browser-only React code
- `src-tauri`: Native Rust backend
- `ai-runtime`: Python AI services

### 3. IPC Communication
- Tauri commands for Rust ↔ React
- HTTP/WebSocket for Rust ↔ Python
- Strict schema validation on all boundaries

### 4. Plugin Architecture
- Sandboxed execution
- Permission-based access control
- Hot-reloadable at runtime

### 5. Test Organization
- Unit tests alongside source code
- Integration tests in dedicated directory
- E2E tests simulate real user workflows

## Next Steps

1. Implement Security Manager (Rust)
2. Build Timeline Engine Core (Rust)
3. Create Hardware Detection Module (Rust + Python)
4. Develop Creative Director Agent (Python)
5. Build React UI Shell (TypeScript)

Each module will be developed with:
- Production code
- Comprehensive tests
- Documentation
- Usage examples
