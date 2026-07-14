# ADR-008: Offline-First with Optional Cloud

## Status

Accepted

## Context

Modern creative tools face a critical design decision: cloud-dependent vs. offline-capable.

Cloud-dependent tools create problems:
1. **Work Interruption**: No internet = no work
2. **Privacy Risks**: Content uploaded to third parties
3. **Latency**: Network round-trips slow operations
4. **Cost**: Cloud compute expenses passed to users
5. **Vendor Lock-in**: Services can shut down or change pricing
6. **Data Sovereignty**: Users lose control of their content

However, cloud services offer benefits:
1. **Massive Scale**: Access to larger models than fit locally
2. **Latest Features**: New AI capabilities without downloads
3. **Collaboration**: Easier multi-user workflows
4. **Backup**: Automatic cloud storage options

Professional tools must balance these competing needs.

## Decision

VID-ED implements **Offline-First Architecture with Opt-In Cloud**:

### Core Principle

**The application must be fully functional without any internet connection.**

Cloud features are additive enhancements that users explicitly enable.

### Feature Classification

| Feature Category | Default | Cloud Option | Notes |
|-----------------|---------|--------------|-------|
| Video Editing | ✅ Local | N/A | Core functionality always local |
| Timeline Engine | ✅ Local | N/A | All editing operations local |
| Speech Recognition | ✅ Local | Optional | Whisper local, cloud for higher accuracy |
| Caption Generation | ✅ Local | Optional | Local LLM, cloud for more languages |
| Object Detection | ✅ Local | Optional | YOLO local, cloud for rare objects |
| Color Correction | ✅ Local | Optional | ONNX models local |
| Audio Enhancement | ✅ Local | Optional | Local processing |
| Motion Tracking | ✅ Local | N/A | OpenCV-based, always local |
| Creative Director | ✅ Local | Optional | Local LLM default, cloud for advanced reasoning |
| Trend Research | ❌ N/A | ✅ Cloud | Requires internet by nature |
| Publishing | ⚠️ Hybrid | ✅ Cloud | Local prep, cloud API for upload |
| AI Image Gen | ❌ N/A | ✅ Cloud | Too large for most local systems |
| AI Video Gen | ❌ N/A | ✅ Cloud | Experimental, cloud-only initially |
| Cloud Render | ❌ N/A | ✅ Cloud | For users without capable hardware |
| Collaboration | ❌ N/A | ✅ Cloud | Real-time sync requires infrastructure |

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                   │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                 FEATURE ROUTER                       │
│                                                      │
│  ┌────────────────────┐    ┌────────────────────┐   │
│  │   LOCAL PROCESSING │    │   CLOUD PROCESSING │   │
│  │                    │    │                    │   │
│  │ • Llama.cpp        │    │ • Cloud APIs       │   │
│  │ • Whisper.cpp      │    │ • User-managed keys│   │
│  │ • ONNX Runtime     │    │ • Explicit opt-in  │   │
│  │ • FFmpeg           │    │ • Per-feature toggle│  │
│  │ • OpenCV           │    │                    │   │
│  └────────────────────┘    └────────────────────┘   │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                    DATA LAYER                        │
│                                                      │
│  ┌────────────────────┐    ┌────────────────────┐   │
│  │   LOCAL STORAGE    │    │   CLOUD STORAGE    │   │
│  │                    │    │                    │   │
│  │ • SQLite (projects)│    │ • User's own cloud │   │
│  │ • LanceDB (vectors)│    │ • Encrypted sync   │   │
│  │ • File system      │    │ • Optional backup  │   │
│  │ • Model cache      │    │                    │   │
│  └────────────────────┘    └────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Connection State Management

```rust
pub enum ConnectivityState {
    Offline,           // No internet connection
    Online,            // Connected, all features available
    Limited,           // Connected but some services unavailable
    CloudDisabled,     // Online but user disabled cloud features
}

pub struct ConnectionManager {
    state: Arc<RwLock<ConnectivityState>>,
    cloud_enabled: Arc<AtomicBool>,
    feature_availability: HashMap<String, FeatureAvailability>,
}

impl ConnectionManager {
    pub fn get_feature_status(&self, feature: &str) -> FeatureStatus {
        let connectivity = self.state.read();
        let cloud_enabled = self.cloud_enabled.load(Ordering::Relaxed);
        
        match FEATURE_REGISTRY.get(feature) {
            Some(FeatureConfig { requires_cloud: false, .. }) => {
                FeatureStatus::Available // Always available locally
            },
            Some(FeatureConfig { requires_cloud: true, .. }) => {
                if !cloud_enabled {
                    FeatureStatus::DisabledByUser
                } else if matches!(*connectivity, ConnectivityState::Offline) {
                    FeatureStatus::RequiresConnection
                } else {
                    FeatureStatus::Available
                }
            },
            None => FeatureStatus::Unknown,
        }
    }
    
    pub async fn check_connectivity(&self) -> ConnectivityState {
        // Check multiple endpoints to determine actual connectivity
        let checks = vec![
            self.check_endpoint("https://www.google.com").await,
            self.check_endpoint("https://api.github.com").await,
            self.check_our_api().await,
        ];
        
        match checks.iter().filter(|r| *r).count() {
            0 => ConnectivityState::Offline,
            1..=2 => ConnectivityState::Limited,
            _ => ConnectivityState::Online,
        }
    }
}
```

### Graceful Degradation

When cloud features become unavailable:

```rust
pub struct FeatureFallback {
    primary: FeatureImplementation,
    fallback: Option<FeatureImplementation>,
}

impl FeatureFallback {
    pub async fn execute(&self, input: FeatureInput) -> Result<FeatureOutput, Error> {
        // Try primary implementation
        match self.primary.execute(input.clone()).await {
            Ok(result) => Ok(result),
            Err(e) if e.is_connection_error() => {
                // Try fallback if available
                if let Some(fallback) = &self.fallback {
                    tracing::warn!("Primary feature failed, using fallback: {}", e);
                    fallback.execute(input).await
                } else {
                    Err(Error::FeatureUnavailable {
                        feature: self.primary.name(),
                        reason: "No internet connection and no local fallback available",
                    })
                }
            },
            Err(e) => Err(e),
        }
    }
}

// Example: Speech-to-text with fallback
let speech_to_text = FeatureFallback {
    primary: FeatureImplementation::CloudWhisper, // Higher accuracy
    fallback: Some(FeatureImplementation::LocalWhisperTiny), // Lower accuracy but works offline
};
```

### User Experience Patterns

#### 1. Clear Status Indicators

```
┌─────────────────────────────────────────┐
│  🟢 All features available             │  ← Online
│  🟡 Limited features (offline mode)    │  ← Offline  
│  🔵 Cloud features disabled            │  ← User disabled
└─────────────────────────────────────────┘
```

#### 2. Feature Availability Tooltips

When hovering over cloud-only features while offline:

```
┌─────────────────────────────────────────┐
│  Trend Research                         │
│  ⚠️ Requires internet connection        │
│                                         │
│  This feature analyzes online trends    │
│  and requires an active connection.     │
│                                         │
│  [Enable Cloud Features] [Dismiss]      │
└─────────────────────────────────────────┘
```

#### 3. Seamless Transition

When connection is lost during operation:

```
Notification: "Internet connection lost. Switching to offline mode."

In-progress cloud tasks:
- Queued for retry when connected
- OR offered local alternative if available
- OR user prompted to save and continue later
```

### Data Synchronization

For users who enable optional cloud sync:

```rust
pub struct SyncEngine {
    local_db: SqliteConnection,
    cloud_client: CloudStorageClient,
    conflict_resolver: ConflictResolver,
}

impl SyncEngine {
    pub async fn sync(&self) -> Result<SyncResult, SyncError> {
        // Get local changes since last sync
        let local_changes = self.local_db.get_changes_since(self.last_sync_timestamp).await?;
        
        // Get remote changes
        let remote_changes = self.cloud_client.get_changes(self.last_sync_timestamp).await?;
        
        // Detect and resolve conflicts
        let conflicts = self.detect_conflicts(&local_changes, &remote_changes)?;
        
        if !conflicts.is_empty() {
            let resolution = self.conflict_resolver.resolve(conflicts).await?;
            // Apply resolution
        }
        
        // Apply changes in correct order
        self.apply_changes(local_changes, remote_changes).await?;
        
        Ok(SyncResult::Success)
    }
}

// Encryption for cloud sync
pub struct EncryptedSync {
    encryption_key: UserMasterKey, // Never leaves device
}

impl EncryptedSync {
    pub fn encrypt_payload(&self, data: &[u8]) -> Vec<u8> {
        // AES-256-GCM encryption
        // Key derived from user password + salt
        // Cloud stores only encrypted blobs
    }
}
```

### Cloud Configuration

Users manage cloud features in settings:

```json
{
  "cloud_settings": {
    "enabled": false,  // Master switch
    "features": {
      "creative_director_cloud": {
        "enabled": false,
        "provider": "openai",  // or anthropic, google, etc.
        "api_key": null,  // User provides
        "model": "gpt-4o"
      },
      "speech_recognition": {
        "enabled": false,
        "prefer_cloud": true,  // Use cloud when available
        "fallback_to_local": true
      },
      "trend_research": {
        "enabled": false,
        "sources": ["youtube", "tiktok", "twitter"]
      },
      "publishing": {
        "enabled": false,
        "platforms": {
          "youtube": { "connected": false },
          "tiktok": { "connected": false },
          "instagram": { "connected": false }
        }
      },
      "cloud_render": {
        "enabled": false,
        "provider": "aws",  // or gcp, azure
        "region": "us-east-1"
      },
      "backup": {
        "enabled": false,
        "frequency": "daily",
        "encrypt": true,
        "provider": "user_choice"  // S3, GCS, Dropbox, etc.
      }
    }
  }
}
```

## Consequences

### Positive

- **Reliability**: Works regardless of internet status
- **Privacy**: Sensitive content never leaves device by default
- **Performance**: No network latency for core operations
- **User Control**: Explicit choice about cloud usage
- **Cost Savings**: No mandatory cloud subscriptions
- **Future-Proof**: Not dependent on any single cloud provider
- **Compliance**: Easier to meet data residency requirements

### Negative

- **Development Complexity**: Must build and maintain dual implementations
- **Testing Burden**: Test all features in online and offline states
- **Model Limitations**: Local models may be less capable than cloud
- **Update Friction**: Model improvements require downloads
- **Storage Requirements**: Local models consume disk space

### Mitigation Strategies

- Design feature abstraction layer to swap implementations easily
- Build automated tests for connectivity state transitions
- Provide clear model comparison so users understand tradeoffs
- Implement efficient model delta updates
- Use quantization to reduce model sizes
- Cache aggressively to minimize repeated downloads

## References

- Local-First Software manifesto (Ink & Switch)
- Figma's offline mode architecture
- Google Docs offline implementation
- Apple Final Cut Pro X library management
- DaVinci Resolve offline workflows
- SQLite sync framework patterns
