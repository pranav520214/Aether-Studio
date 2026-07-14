# ADR-001: Local-First Architecture

## Status

Accepted

## Context

Modern AI video editing tools rely heavily on cloud processing, which creates several problems:

1. **Privacy concerns**: Users must upload sensitive content to third-party servers
2. **Latency**: Network round-trips slow down creative workflows
3. **Cost**: Cloud GPU compute is expensive at scale
4. **Offline limitations**: Tools become unusable without internet
5. **Vendor lock-in**: Users lose access to their projects if services shut down

Professional video editors (Premiere Pro, DaVinci Resolve) have proven that local-first is viable for demanding workloads.

## Decision

VID-ED will be architected as a **Local-First AI Creative Operating System**:

1. **Default behavior**: All AI inference, video processing, and data storage happens locally on the user's machine
2. **Cloud as optional**: Cloud AI services (image generation, video generation, cloud rendering) are ONLY used when explicitly requested by the user
3. **Offline guarantee**: The application remains fully functional without internet connectivity
4. **Data sovereignty**: All user data, projects, and memories stay on the local device unless explicitly exported
5. **Hybrid capability**: When cloud features are enabled, they operate as extensions, not replacements, for local capabilities

### Implementation Requirements

- All core agents run locally via llama.cpp, whisper.cpp, and ONNX Runtime
- SQLite and LanceDB store data locally with encryption
- FFmpeg and OpenCV handle all video processing on-device
- Model files are downloaded once and cached indefinitely
- Cloud API keys are user-provided, never embedded in the application

## Consequences

### Positive

- **Privacy by design**: No user content leaves the device without explicit consent
- **Performance**: No network latency for AI operations
- **Cost efficiency**: Users leverage their own hardware instead of paying for cloud compute
- **Reliability**: Works offline, immune to service outages
- **Trust**: Transparent about what runs locally vs. remotely

### Negative

- **Hardware dependency**: Performance varies based on user's machine
- **Model size limits**: Must carefully select models that fit in consumer VRAM
- **Update complexity**: Model improvements require user downloads
- **Feature ceiling**: Some cutting-edge AI features may be unavailable locally initially

### Mitigation Strategies

- Implement hardware detection to adapt model selection dynamically
- Use quantized models (4-bit, 8-bit) to reduce memory footprint
- Build a model manager for easy updates and rollbacks
- Design architecture so cloud providers can be plugged in as optional backends

## References

- [Local-First Software Manifesto](https://www.inkandswitch.com/local-first/)
- Adobe Premiere Pro architecture analysis
- DaVinci Resolve performance benchmarks
- llama.cpp performance on consumer GPUs
