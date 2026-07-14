# Aether Studio (VID-ED)

**Local AI Agentic Video Production Platform**

An open-source, local-first AI video production platform that combines collaborative AI agents, computer vision, speech intelligence, timeline reasoning, and deterministic rendering to automate professional video editing while keeping users in control.

## 🎯 Vision

Aether Studio empowers creators with an intelligent video editing ecosystem where:
- **AI Agents collaborate** like a professional production team
- **Everything runs locally** on your hardware for privacy and speed
- **Professional quality** meets automated intelligence
- **You stay in control** while AI handles the heavy lifting

## 🏗️ Architecture

```
USER → ORCHESTRATOR AGENT → SPECIALIZED AGENTS → TIMELINE ENGINE → RENDER ENGINE
```

### Core Components

#### 1. **Orchestrator/Director Agent**
- Runs locally (Qwen 3B / Phi / Gemma)
- Understands user goals and builds editing plans
- Schedules specialized agents and manages memory
- Adapts to available hardware automatically

#### 2. **Video Understanding Layer**
- **Speech**: Whisper.cpp, Speech Diarization, Silero VAD
- **Vision**: Scene Detection, OCR, YOLO11, MediaPipe, Optical Flow, Face Tracking
- **Audio**: Emotion detection, audio analysis
- All results cached in `video.cache.json` - no redundant re-analysis

#### 3. **Specialized Editing Agents**
- **Story Agent**: Hook detection, retention analysis, clip ranking
- **Caption Agent**: Subtitle timing, word highlighting, emoji placement
- **Motion Agent**: Auto zoom, pan, reframe, crop
- **Audio Agent**: Noise removal, EQ, loudness normalization, ducking
- **Voice Agent**: Voice calibration, lip sync, AI voice clone (optional)
- **Color Agent**: Exposure, white balance, LUT suggestions, color matching
- **VFX Agent**: Motion blur, camera shake, particles, glow, speed ramps
- **Thumbnail Agent**: Automatic thumbnail generation
- **Music Agent**: Background music selection and mixing
- **B-roll Agent**: Intelligent B-roll insertion
- **Shorts Agent**: Vertical video optimization

#### 4. **Shared Timeline Engine**
- JSON-based timeline representation
- Tracks, transitions, effects, masks, captions, animations, keyframes
- All agents edit the timeline - never raw pixels
- Deterministic and version-controlled

#### 5. **Render Engine**
- FFmpeg + OpenCV + ONNX Runtime + MoviePy
- Export to Premiere XML, DaVinci XML
- GPU acceleration support
- Deterministic rendering for reproducibility

#### 6. **Memory System**
- Creator profiles and brand memory
- Editing preferences and style guides
- Local vector database with embeddings
- Persistent learning across projects

#### 7. **Hardware Adaptation**
- Automatic model selection based on available resources:
  - 8GB RAM → 0.5B models
  - 16GB RAM → 3B models
  - 32GB RAM → 7B models
- GPU/CPU optimization
- Real-time performance monitoring

## 📁 Project Structure

```
aether-studio/
├── stitch_vid_ed_ai_video_os/
│   ├── vid_ed_backend/          # FastAPI backend service
│   │   ├── core/                # Core services (LLM, security, jobs)
│   │   └── schemas/             # Pydantic data models
│   ├── luminous_editorial/      # Design system & UI components
│   ├── vid_ed_creative_studio_editor/  # Main editor interface
│   └── vid_ed_home_dashboard/   # User dashboard
├── VID-ED.md                    # Architecture documentation
├── LICENSE                      # Apache 2.0
└── README.md                    # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- FFmpeg installed on your system
- GPU recommended (NVIDIA with CUDA support)
- Minimum 8GB RAM (16GB+ recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/aether-studio.git
cd aether-studio/stitch_vid_ed_ai_video_os

# Install backend dependencies
cd vid_ed_backend
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload
```

### Hardware Requirements

| RAM | Recommended Models | Performance |
|-----|-------------------|-------------|
| 8GB | 0.5B models | Basic editing |
| 16GB | 3B models | Standard workflow |
| 32GB+ | 7B models | Professional grade |

## 🤖 How It Works

1. **User Input**: Provide natural language instructions (e.g., "Make this like Apple + MrBeast but optimized for Instagram Reels")

2. **Orchestration**: The Director Agent parses your request and creates an editing plan

3. **Analysis**: Video Understanding Layer analyzes your footage once and caches all metadata

4. **Collaboration**: Specialized agents work together on the shared timeline:
   - Story Agent identifies the best moments
   - Caption Agent adds engaging subtitles
   - Motion Agent creates dynamic movement
   - Audio Agent perfects the sound
   - And more...

5. **Rendering**: The deterministic render engine produces your final video

6. **Optional Cloud**: Only when explicitly requested (AI B-roll, AI actors, etc.)

## 🎨 Design Philosophy

Built on the **Luminous Editorial** design system:
- **Clarity**: Focused environment for high-fidelity editing
- **Minimalist Utility**: Corporate Modernism meets Apple-level refinement
- **Content-First**: Generous whitespace lets your videos shine
- **Tonal Layering**: Sophisticated elevation through subtle shadows and borders

## 🔒 Privacy First

- **100% Local Processing**: All video analysis and editing happens on your machine
- **No Data Upload**: Your content never leaves your computer unless you explicitly choose cloud features
- **Open Source**: Transparent codebase you can audit and modify

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **LLM**: Ollama (Qwen, Phi, Gemma)
- **Computer Vision**: OpenCV, MediaPipe, YOLO11
- **Speech**: Whisper.cpp, Silero VAD
- **Video Processing**: FFmpeg, MoviePy
- **Vector Database**: ChromaDB
- **Frontend**: React/TypeScript (coming soon)

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

We welcome contributions! This is an active project building the future of AI-powered video editing.

## 📞 Support

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Built for creators who demand both quality and control.**
