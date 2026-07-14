# ADR-005: Hardware Adaptive Model Loading

## Status

Accepted

## Context

AI video editing workloads vary dramatically based on hardware capabilities:

- **Low-end**: Integrated GPU, 8GB RAM, no CUDA
- **Mid-range**: Dedicated GPU (GTX/RTX 3060), 16-32GB RAM, 6-8GB VRAM
- **High-end**: Multiple GPUs (RTX 4090), 64GB+ RAM, 24GB+ VRAM
- **Apple Silicon**: Unified memory architecture, Metal acceleration

A one-size-fits-all approach fails because:
1. Large models crash low-end systems
2. Small models underutilize high-end hardware
3. Users don't understand model quantization or hardware requirements
4. Manual configuration creates friction and support burden

Professional apps (DaVinci Resolve) automatically detect hardware and adjust settings.

## Decision

VID-ED implements **Automatic Hardware Detection with Adaptive Model Loading**:

### Hardware Detection Agent

On startup, the system profiles the machine:

```rust
pub struct HardwareProfile {
    pub cpu: CpuInfo,
    pub gpu: Vec<GpuInfo>,
    pub ram: MemoryInfo,
    pub vram: Vec<VramInfo>,
    pub disk: DiskInfo,
    pub capabilities: HardwareCapabilities,
}

pub struct HardwareCapabilities {
    pub cuda: bool,
    pub directml: bool,
    pub metal: bool,
    pub vulkan: bool,
    pub avx2: bool,
    pub avx512: bool,
    pub tensor_cores: bool,
    pub ray_tracing: bool,
}

pub enum PerformanceTier {
    Minimum,      // Can run basic edits, small models only
    Recommended,  // Good performance with medium models
    High,         // Excellent performance with large models
    Professional, // Can run all models at full quality
}
```

### Detection Process

```
┌─────────────────┐
│ System Startup  │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Detect CPU     │ → Cores, threads, SIMD extensions
└────────┬────────┘
         ↓
┌─────────────────┐
│  Detect GPU(s)  │ → Vendor, VRAM, compute APIs
└────────┬────────┘
         ↓
┌─────────────────┐
│  Measure RAM    │ → Total, available, speed
└────────┬────────┘
         ↓
┌─────────────────┐
│  Benchmark Disk │ → Read/write speeds
└────────┬────────┘
         ↓
┌─────────────────┐
│ Compute Tier &  │
│ Recommendations │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Load Appropriate│
│  Model Versions │
└─────────────────┘
```

### Model Selection Matrix

| Performance Tier | LLM (Creative Director) | Whisper (Speech) | Vision (Detection) | Max Concurrent Models |
|-----------------|------------------------|------------------|-------------------|----------------------|
| Minimum | Phi-3 Mini (4-bit) | Whisper Tiny | MobileSAM | 1 |
| Recommended | Mistral 7B (8-bit) | Whisper Base | YOLOv8 Nano | 2 |
| High | Mistral 7B (4-bit) | Whisper Medium | YOLOv8 Small | 3 |
| Professional | Mixtral 8x7B (4-bit) | Whisper Large | YOLOv8 Large | 4+ |

### Model Loading Strategy

```rust
pub struct ModelManager {
    loaded_models: HashMap<String, LoadedModel>,
    model_cache: ModelCache,
    memory_budget: MemoryBudget,
}

impl ModelManager {
    pub async fn load_model(&mut self, model_spec: ModelSpec) -> Result<(), ModelError> {
        // Check if already loaded
        if let Some(model) = self.loaded_models.get(&model_spec.id) {
            return Ok(());
        }
        
        // Check memory budget
        let required_vram = model_spec.estimated_vram();
        if !self.memory_budget.can_allocate(required_vram) {
            // Try to unload lower-priority models
            self.evict_low_priority_models(required_vram)?;
        }
        
        // Select optimal variant based on hardware
        let variant = self.select_variant(&model_spec);
        
        // Load model with appropriate backend
        let model = match variant.backend {
            Backend::Cuda => self.load_cuda_model(&variant).await?,
            Backend::DirectML => self.load_directml_model(&variant).await?,
            Backend::Metal => self.load_metal_model(&variant).await?,
            Backend::Cpu => self.load_cpu_model(&variant).await?,
        };
        
        self.loaded_models.insert(model_spec.id.clone(), model);
        Ok(())
    }
    
    pub async fn unload_model(&mut self, model_id: &str) -> Result<(), ModelError> {
        if let Some(model) = self.loaded_models.remove(model_id) {
            // Free VRAM immediately
            drop(model);
            // Clear from cache if needed
            self.model_cache.clear(model_id)?;
        }
        Ok(())
    }
    
    pub async fn unload_all_idle_models(&mut self) -> Result<(), ModelError> {
        // Keep only recently used models in memory
        let idle_threshold = Duration::from_secs(300); // 5 minutes
        
        let idle_models: Vec<_> = self.loaded_models
            .iter()
            .filter(|(_, m)| m.last_used.elapsed() > idle_threshold)
            .map(|(id, _)| id.clone())
            .collect();
        
        for model_id in idle_models {
            self.unload_model(&model_id).await?;
        }
        
        Ok(())
    }
}
```

### Memory Budget Calculation

```rust
impl MemoryBudget {
    pub fn calculate(hardware: &HardwareProfile) -> Self {
        let total_vram = hardware.gpu.iter()
            .map(|g| g.vram_bytes)
            .sum::<u64>();
        
        let total_ram = hardware.ram.total_bytes;
        
        // Reserve 25% of VRAM for system/display
        let available_vram = (total_vram as f64 * 0.75) as u64;
        
        // Reserve 4GB of RAM for OS and other apps
        let available_ram = total_ram.saturating_sub(4 * 1024 * 1024 * 1024);
        
        Self {
            vram_budget: available_vram,
            ram_budget: available_ram,
            vram_used: 0,
            ram_used: 0,
        }
    }
    
    pub fn can_allocate(&self, bytes: u64) -> bool {
        self.vram_used + bytes <= self.vram_budget
    }
}
```

### Model Variants Registry

```json
{
  "creative_director": {
    "variants": [
      {
        "id": "phi3-mini-4bit",
        "name": "Phi-3 Mini (4-bit)",
        "size_mb": 2400,
        "estimated_vram_mb": 3000,
        "min_tier": "minimum",
        "backend": ["cpu", "cuda", "directml"],
        "quantization": "q4_k_m"
      },
      {
        "id": "mistral-7b-8bit",
        "name": "Mistral 7B (8-bit)",
        "size_mb": 7800,
        "estimated_vram_mb": 9000,
        "min_tier": "recommended",
        "backend": ["cuda", "directml"],
        "quantization": "q8_0"
      },
      {
        "id": "mistral-7b-4bit",
        "name": "Mistral 7B (4-bit)",
        "size_mb": 4200,
        "estimated_vram_mb": 5000,
        "min_tier": "high",
        "backend": ["cuda", "directml", "metal"],
        "quantization": "q4_k_m"
      },
      {
        "id": "mixtral-8x7b-4bit",
        "name": "Mixtral 8x7B (4-bit)",
        "size_mb": 26000,
        "estimated_vram_mb": 30000,
        "min_tier": "professional",
        "backend": ["cuda", "metal"],
        "quantization": "q4_k_m"
      }
    ]
  }
}
```

### Runtime Adaptation

The system continuously monitors resource usage:

```rust
pub struct ResourceMonitor {
    vram_usage: Arc<Mutex<f64>>,
    ram_usage: Arc<Mutex<f64>>,
    model_load_avg: Arc<Mutex<Duration>>,
}

impl ResourceMonitor {
    pub fn spawn_monitor(manager: Arc<ModelManager>) -> JoinHandle<()> {
        tokio::spawn(async move {
            let mut interval = tokio::time::interval(Duration::from_secs(5));
            
            loop {
                interval.tick().await;
                
                let vram_percent = Self::get_vram_usage();
                let ram_percent = Self::get_ram_usage();
                
                // Alert user if running low
                if vram_percent > 0.9 || ram_percent > 0.9 {
                    tracing::warn!("Memory pressure detected: VRAM {:.1}%, RAM {:.1}%", 
                                   vram_percent * 100.0, ram_percent * 100.0);
                    
                    // Automatically unload idle models
                    if let Err(e) = manager.unload_all_idle_models().await {
                        tracing::error!("Failed to free memory: {}", e);
                    }
                }
            }
        })
    }
}
```

## Consequences

### Positive

- **Accessibility**: Works on wide range of hardware
- **Performance**: Maximizes capabilities of each machine
- **User Experience**: No manual configuration required
- **Stability**: Prevents OOM crashes through proactive management
- **Efficiency**: Unloads models when not needed
- **Transparency**: Users can see what's running and why

### Negative

- **Complexity**: Significant engineering effort for detection logic
- **Testing Burden**: Must test on many hardware configurations
- **Edge Cases**: Unusual hardware may be misclassified
- **Model Management**: Need to maintain multiple variants per model
- **Download Size**: Multiple model variants increase initial download

### Mitigation Strategies

- Download model variants on-demand, not bundled
- Implement robust fallback chains (if CUDA fails, try DirectML, then CPU)
- Provide manual override for advanced users
- Build comprehensive hardware test matrix
- Use community feedback to improve detection heuristics
- Cache model selection decisions to avoid re-detection

## Implementation Details

### Hardware Detection Libraries

```toml
[dependencies]
# CPU/GPU detection
sysinfo = "0.30"
nvml-wrapper = "0.9"          # NVIDIA GPU monitoring
wmi = "0.12"                  # Windows hardware info

# Benchmarking
criterion = "0.5"

# Model inference
llama-cpp-rs = { git = "https://github.com/ggerganov/llama.cpp" }
whisper-rs = { git = "https://github.com/ggerganov/whisper.cpp" }
ort = "2.0"                   # ONNX Runtime
```

### User Interface

Settings panel shows:
- Detected hardware summary
- Current performance tier
- Active models and their memory usage
- Option to manually select model variants
- Memory usage graphs
- Recommendations for upgrades

## References

- NVIDIA CUDA Best Practices Guide
- llama.cpp hardware detection implementation
- DaVinci Resolve system requirements analysis
- Adobe Premiere Pro Mercury Playback Engine documentation
- ONNX Runtime execution provider selection
- Windows DirectML documentation
