# Privantrix AI OS

Production-quality bootstrap installer for an advanced local AI development environment.

## Features

- **Automatic Installation**: One-command setup of complete AI infrastructure
- **Hardware Detection**: Automatic detection and benchmarking of CPU, GPU, RAM
- **Model Router**: Intelligent model selection based on capabilities and latency
- **Memory System**: Multi-tier memory (working, session, project, long-term)
- **Planner**: Execution graph creation with milestone tracking
- **LM Studio Integration**: Full API client with streaming support
- **Database Layer**: SQLite + ChromaDB for structured and vector storage
- **Dashboard**: Real-time web dashboard for monitoring
- **CLI Interface**: Full command-line interface for all operations

## Directory Structure

```
D:\Privantrix-AI-OS\
├── AI-OS/
│   ├── src/           # Source code
│   ├── configs/       # Configuration files
│   ├── database/      # SQLite databases
│   ├── embeddings/    # ChromaDB vector store
│   ├── memory/        # Memory storage
│   ├── projects/      # Project files
│   ├── logs/          # Log files
│   ├── checkpoints/   # System checkpoints
│   ├── benchmarks/    # Benchmark results
│   └── ...
```

## Quick Start

### Windows

```powershell
cd D:\Privantrix-AI-OS\AI-OS
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python bootstrap.py
```

### Linux/Mac

```bash
cd /path/to/Privantrix-AI-OS/AI-OS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bootstrap.py
```

## CLI Usage

```bash
# Initialize system
privantrix init

# Run hardware detection
privantrix hardware detect

# Check LM Studio status
privantrix lmstudio check

# Start dashboard
privantrix dashboard start

# Run benchmarks
privantrix benchmark run
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
PRIVANTRIX_BASE_DIR=D:/Privantrix-AI-OS/AI-OS
PRIVANTRIX_ENV=development
LMSTUDIO_HOST=localhost
LMSTUDIO_PORT=1234
LOG_LEVEL=INFO
```

## Requirements

- Python 3.10+
- Windows 10/11 or Linux
- 8GB+ RAM recommended
- NVIDIA GPU with CUDA (optional, for GPU acceleration)

## License

MIT License
