                                         VID-ED
                    Local AI Agentic Video Production Platform
═══════════════════════════════════════════════════════════════════════════════

                         USER
                           │
          "Make this like Apple + MrBeast
       but optimized for Instagram Reels."
                           │
                           ▼
═══════════════════════════════════════════════════════════════════════════════
                  ORCHESTRATOR / DIRECTOR AGENT
          (Qwen 3B / Phi / Gemma running locally)
═══════════════════════════════════════════════════════════════════════════════
                           │
      Understand Goal
      Build Editing Plan
      Schedule Agents
      Manage Memory
      Hardware Optimization
                           │
───────────────────────────┼──────────────────────────────────────────────────
                           │
        ┌──────────────────┼────────────────────┐
        │                  │                    │
        ▼                  ▼                    ▼

Research Agent      Story Agent         Brand Agent
(Local Cache)      (LLM)               (Rules + LLM)

        │                  │                    │

Local Trend DB      Timeline Plan      Brand Guidelines
Embeddings          Hook Analysis      Fonts
Creator Profiles    Pacing             Colors
Knowledge Base      CTA                Logos

───────────────────────────┼──────────────────────────────────────────────────
                           ▼
═══════════════════════════════════════════════════════════════════════════════
                   VIDEO UNDERSTANDING LAYER
═══════════════════════════════════════════════════════════════════════════════

Whisper.cpp
Speech Diarization
Silero VAD
Scene Detection
OCR
YOLO11
MediaPipe
Optical Flow
Face Tracking
Emotion
Audio Analysis

↓

Single Metadata Cache

video.cache.json

↓

No model ever re-analyzes the video.

═══════════════════════════════════════════════════════════════════════════════
                  SPECIALIZED EDITING AGENTS
═══════════════════════════════════════════════════════════════════════════════

Story Agent
├── Hook Detection
├── Retention
├── Clip Ranking

Caption Agent
├── Subtitle Timing
├── Highlight Words
├── Emoji Placement

Motion Agent
├── Auto Zoom
├── Pan
├── Reframe
├── Crop

Audio Agent
├── Noise Removal
├── EQ
├── Loudness
├── Ducking
├── Voice Enhancement

Voice Agent
├── Voice Calibration
├── Lip Sync Alignment
├── AI Voice Clone (optional)
├── Pronunciation Fix

Color Agent
├── Exposure
├── White Balance
├── LUT Suggestion
├── Color Match

VFX Agent
├── Motion Blur
├── Camera Shake
├── Particles
├── Glow
├── Speed Ramps
├── Mask Tracking

Thumbnail Agent

Music Agent

B-roll Agent

Shorts Agent

═══════════════════════════════════════════════════════════════════════════════
                     SHARED TIMELINE ENGINE
═══════════════════════════════════════════════════════════════════════════════

Timeline JSON

Tracks
Transitions
Effects
Masks
Captions
Animations
Keyframes
Audio Layers

Every agent edits THIS.

Never raw pixels.

═══════════════════════════════════════════════════════════════════════════════
                  DETERMINISTIC RENDER ENGINE
═══════════════════════════════════════════════════════════════════════════════

FFmpeg

+

OpenCV

+

ONNX Runtime

+

MoviePy

+

Premiere XML

+

DaVinci XML

+

GPU Acceleration

═══════════════════════════════════════════════════════════════════════════════
                    OPTIONAL CLOUD SERVICES
═══════════════════════════════════════════════════════════════════════════════

ONLY WHEN USER ASKS

Generate Missing B-roll

↓

Claude API / Veo / Imagen / Runway / Flux

Generate AI Actor

Generate AI Background

Generate AI Product Shot

Generate AI Voice

Everything else stays LOCAL.

═══════════════════════════════════════════════════════════════════════════════
                        MEMORY SYSTEM
═══════════════════════════════════════════════════════════════════════════════

Creator Profile

Brand Memory

Editing Preferences

Transition Style

Caption Style

Music Style

Frequently Used Assets

Previous Projects

Embeddings

Local Vector Database

═══════════════════════════════════════════════════════════════════════════════
                    HARDWARE ADAPTATION LAYER
═══════════════════════════════════════════════════════════════════════════════

Detect CPU

Detect GPU

Detect RAM

↓

Choose Models Automatically

8 GB
↓

0.5B Models

16 GB
↓

3B Models

32 GB
↓

7B Models

RTX
↓

GPU

No GPU
↓

CPU Optimized

═══════════════════════════════════════════════════════════════════════════════