# ADR-002: Tauri + Rust + React Tech Stack

## Status

Accepted

## Context

Building a production-grade video editing application requires careful technology selection. We evaluated multiple stacks:

### Considered Options

1. **Electron + Node.js + React**
   - Pros: Mature ecosystem, large developer pool
   - Cons: High memory footprint, slower performance, security concerns with Node.js

2. **Native Windows (C++/WinRT) + WinUI 3**
   - Pros: Best performance, native look and feel
   - Cons: Windows-only, steep learning curve, slower development

3. **Flutter + Rust**
   - Pros: Good performance, cross-platform
   - Cons: Less mature for desktop, limited video editing ecosystem

4. **Tauri + Rust + React**
   - Pros: Small bundle size, excellent performance, strong security, cross-platform
   - Cons: Younger ecosystem, requires Rust expertise

5. **Qt + C++**
   - Pros: Proven in professional apps (DaVinci Resolve uses Qt)
   - Cons: Licensing complexity, larger binaries, C++ complexity

## Decision

VID-ED will use **Tauri v2 + Rust + React + TypeScript**:

### Architecture Layers

```
┌─────────────────────────────────────┐
│         React + TypeScript          │  ← UI Layer
│         (Renderer Process)          │
├─────────────────────────────────────┤
│         Tauri Commands              │  ← IPC Bridge
├─────────────────────────────────────┤
│           Rust Core                 │  ← Application Logic
│    - Timeline Engine                │
│    - Render Coordinator             │
│    - Plugin Manager                 │
│    - Security Manager               │
├─────────────────────────────────────┤
│        Python AI Runtime            │  ← AI Inference
│    (via subprocess/IPC)             │
├─────────────────────────────────────┤
│     FFmpeg / OpenCV / ONNX          │  ← Native Libraries
└─────────────────────────────────────┘
```

### Justification

1. **Security First**
   - Tauri's security model is superior to Electron
   - No arbitrary JavaScript execution in system context
   - Built-in CSP and protocol isolation
   - Smaller attack surface (no Node.js in renderer)

2. **Performance**
   - Rust provides memory safety without garbage collection pauses
   - WebView2 on Windows offers near-native rendering performance
   - Direct FFI calls to FFmpeg, OpenCV without overhead
   - Efficient multi-threading for video processing

3. **Bundle Size**
   - Tauri apps: ~5-10 MB base
   - Electron apps: ~150-200 MB base
   - Critical for distribution and updates

4. **Cross-Platform Strategy**
   - Windows 11 (primary target)
   - Linux (secondary, well-supported by Tauri)
   - macOS (future, Apple Silicon optimization)

5. **Developer Experience**
   - React ecosystem for UI components
   - TypeScript for type safety across the stack
   - Rust's package manager (Cargo) for dependency management
   - Hot reload support in development

6. **Enterprise Readiness**
   - Strong typing end-to-end
   - Comprehensive testing frameworks (Rust + Jest + React Testing Library)
   - CI/CD integration via GitHub Actions
   - Code signing and notarization support

## Consequences

### Positive

- **Security**: Reduced attack surface, no Node.js vulnerabilities
- **Performance**: Native-speed backend, efficient memory usage
- **Distribution**: Small downloads, faster updates
- **Type Safety**: TypeScript + Rust catch errors at compile time
- **Future-proof**: Backed by Microsoft, AWS, and major contributors

### Negative

- **Learning Curve**: Team needs Rust expertise
- **Ecosystem Maturity**: Tauri plugins less mature than Electron
- **WebView Dependency**: Relies on system WebView2 (Windows) or WebKit (Linux/macOS)
- **Python Integration**: Requires careful IPC design between Rust and Python

### Mitigation Strategies

- Invest in Rust training and documentation
- Build internal Tauri plugin wrappers for common functionality
- Detect and prompt for WebView2 installation on Windows
- Design robust Rust ↔ Python IPC with message queuing and error handling
- Create comprehensive integration tests for cross-language boundaries

## Implementation Details

### Rust Crates (Planned)

```toml
[dependencies]
tauri = "2.0"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1.0", features = ["full"] }
sqlx = { version = "0.7", features = ["sqlite", "runtime-tokio-rustls"] }
lancedb = "0.1"
ffmpeg-next = "7.0"
opencv = "0.90"
tracing = "0.1"
thiserror = "1.0"
uuid = { version = "1.0", features = ["v4"] }
chrono = "0.4"
```

### React Packages (Planned)

```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.0",
    "zustand": "^4.0",
    "react-router-dom": "^6.0",
    "@radix-ui/*": "latest",
    "framer-motion": "^11.0",
    "tailwindcss": "^3.0"
  }
}
```

### Python Dependencies (Planned)

```txt
llama-cpp-python
openai-whisper
onnxruntime-gpu
opencv-python
numpy
pydantic
fastapi
uvicorn
```

## References

- [Tauri Documentation](https://tauri.app)
- [Tauri vs Electron Benchmarks](https://tauri.app/blog/2022/09/01/tauri-1-0)
- [Rust for JavaScript Developers](https://rust-for-js-devs.github.io/)
- Adobe Premiere Pro plugin architecture analysis
- DaVinci Resolve performance profiling reports
