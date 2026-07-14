# CLAUDE.md - Privantrix AI OS

## Project Overview

Privantrix AI OS is a production-quality bootstrap installer for an advanced local AI development environment. It provides automatic installation, configuration, and initialization of AI infrastructure components.

## Quick Commands

```bash
# Initialize the system
python bootstrap.py

# CLI usage
python main.py init          # Run bootstrap
python main.py hardware      # Detect hardware
python main.py lmstudio      # Check LM Studio status
python main.py config        # Show configuration
python main.py verify        # Verify installation
```

## Key Directories

- `src/` - Core source code modules
- `configs/` - Configuration files
- `database/` - SQLite databases
- `embeddings/` - ChromaDB vector store
- `memory/` - Memory JSON storage
- `projects/` - Project-specific data
- `logs/` - Log files
- `scripts/` - Utility scripts

## Core Modules

| Module | Purpose |
|--------|---------|
| `config.py` | Configuration management with Pydantic |
| `hardware.py` | Hardware detection and benchmarking |
| `database.py` | SQLite + ChromaDB management |
| `memory.py` | Multi-tier memory system |
| `router.py` | Intelligent model routing |
| `planner.py` | Task planning and milestones |
| `lmstudio.py` | LM Studio API client |
| `logging.py` | Centralized logging |
| `bootstrap.py` | Installation automation |
| `main.py` | CLI entry point |

## Development Guidelines

1. **Type Hints**: Use type hints for all function signatures
2. **Error Handling**: Wrap external calls in try/except with logging
3. **Logging**: Use the logging module, not print statements
4. **Configuration**: Load from config files, not hardcoded values
5. **Memory Management**: Store important state in appropriate memory tier
6. **Checkpoints**: Save checkpoints at milestones

## Testing

```bash
pip install -e ".[dev]"
pytest tests/
```

## Architecture Principles

- **Modular**: Each component is independent and replaceable
- **Configurable**: All settings exposed through configuration
- **Restart-safe**: State persisted for recovery
- **Local-first**: All data stored on D: drive
- **No telemetry**: No external data transmission

## Common Tasks

### Add a new model to router
Edit `configs/models.json` or use the router API:
```python
from src.router import ModelRouter
router = ModelRouter()
router.register_model("my-model", "Model Name", "http://localhost:1234")
```

### Search memory
```python
from src.memory import init_memory
mem = init_memory()
results = mem.search_memory("query text")
```

### Create a checkpoint
```python
from src.planner import init_planner
planner = init_planner()
planner.save_checkpoint("milestone_name")
```

## Dependencies

Core dependencies are in `requirements.txt`. Install with:
```bash
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and configure as needed.
