# ADR-006: Plugin Sandbox Security

## Status

Accepted

## Context

A plugin system is essential for extensibility, but plugins introduce significant security risks:

1. **Arbitrary Code Execution**: Malicious plugins could steal data or damage systems
2. **Privilege Escalation**: Plugins might access resources beyond their intended scope
3. **Data Exfiltration**: Plugins could send user content to external servers
4. **System Instability**: Poorly written plugins could crash the host application
5. **Supply Chain Attacks**: Compromised plugin dependencies affect all users

Professional platforms (VS Code, Figma, OBS) implement strict sandboxing for plugins.

## Decision

VID-ED implements a **Multi-Layer Plugin Security Model**:

### Security Architecture

```
┌─────────────────────────────────────────────────────┐
│                  USER PROJECT                       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              PLUGIN HOST (Rust Process)             │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Plugin A  │  │   Plugin B  │  │   Plugin C  │  │
│  │  (Sandbox)  │  │  (Sandbox)  │  │  (Sandbox)  │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
│         │                │                │         │
│         └────────────────┼────────────────┘         │
│                          ↓                          │
│              ┌─────────────────────┐                │
│              │  Security Manager   │                │
│              │  - Path Validation  │                │
│              │  - Permission Check │                │
│              │  - Rate Limiting    │                │
│              │  - Resource Quotas  │                │
│              └─────────────────────┘                │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                 CORE APPLICATION                    │
│           (Limited API Surface Exposure)            │
└─────────────────────────────────────────────────────┘
```

### Sandboxing Strategy

Plugins run in isolated subprocesses with restricted capabilities:

```rust
pub struct PluginSandbox {
    plugin_id: String,
    process: Child,
    ipc_channel: PluginChannel,
    permissions: PluginPermissions,
    resource_limiter: ResourceLimiter,
}

pub struct PluginPermissions {
    pub filesystem: FsAccess,
    pub network: NetworkAccess,
    pub timeline: TimelineAccess,
    pub media: MediaAccess,
    pub ai_models: AiModelAccess,
    pub system: SystemAccess,
}

pub enum FsAccess {
    None,
    ReadOnly(PathBuf),      // Can only read from specific directory
    ReadWrite(PathBuf),     // Can read/write in sandbox directory
    Full,                   // Not recommended, requires explicit approval
}

pub enum NetworkAccess {
    Disabled,
    AllowList(Vec<String>), // Specific domains only
    Enabled,                // Full internet access (requires approval)
}
```

### Capability-Based Security

Plugins declare required permissions in manifest:

```json
{
  "name": "color-grading-plugin",
  "version": "1.0.0",
  "description": "Advanced color grading tools",
  "permissions": {
    "filesystem": {
      "scope": "plugin_data",
      "read": true,
      "write": true
    },
    "network": {
      "enabled": false
    },
    "timeline": {
      "read": true,
      "write": true,
      "operations": ["add_effect", "adjust_color"]
    },
    "media": {
      "read_project_media": true,
      "import_external": false
    },
    "ai_models": {
      "allowed_models": ["color_enhancement_v1"],
      "max_concurrent_inferences": 2
    },
    "system": {
      "max_memory_mb": 512,
      "max_cpu_percent": 25,
      "timeout_seconds": 30
    }
  },
  "api_version": "1.0"
}
```

### Security Manager Implementation

```rust
pub struct SecurityManager {
    sandbox_root: PathBuf,
    allowed_paths: HashSet<PathBuf>,
    plugin_policies: HashMap<String, PluginPolicy>,
}

impl SecurityManager {
    pub fn new(sandbox_root: PathBuf) -> Self {
        Self {
            sandbox_root,
            allowed_paths: HashSet::new(),
            plugin_policies: HashMap::new(),
        }
    }
    
    pub fn sanitize_path(&self, requested_path: &Path) -> Result<PathBuf, SecurityError> {
        // Resolve to absolute path
        let absolute = requested_path.canonicalize()
            .or_else(|_| Ok(requested_path.to_path_buf()))?;
        
        // Ensure path is within allowed directories
        let is_allowed = self.allowed_paths.iter()
            .any(|allowed| absolute.starts_with(allowed));
        
        if !is_allowed {
            return Err(SecurityError::PathViolation {
                requested: absolute,
                reason: "Path outside allowed directories"
            });
        }
        
        // Check for path traversal attempts
        if requested_path.components()
            .any(|c| c.as_os_str() == "..") 
        {
            return Err(SecurityError::PathTraversalDetected);
        }
        
        Ok(absolute)
    }
    
    pub fn validate_plugin_request(
        &self,
        plugin_id: &str,
        request: &PluginRequest
    ) -> Result<(), SecurityError> {
        let policy = self.plugin_policies.get(plugin_id)
            .ok_or(SecurityError::UnknownPlugin)?;
        
        match request {
            PluginRequest::ReadFile { path } => {
                self.sanitize_path(path)?;
                if !policy.permissions.filesystem.read {
                    return Err(SecurityError::PermissionDenied("read"));
                }
            },
            PluginRequest::ExecuteCommand { command, args } => {
                // Never allow arbitrary shell execution
                if !policy.permissions.system.allow_subprocess {
                    return Err(SecurityError::PermissionDenied("subprocess"));
                }
                // Validate command against allowlist
                if !policy.allowed_commands.contains(command) {
                    return Err(SecurityError::CommandNotAllowed(command.clone()));
                }
                // Validate arguments (no shell injection)
                for arg in args {
                    if arg.contains([';', '|', '&', '$', '`']) {
                        return Err(SecurityError::PotentialInjection(arg.clone()));
                    }
                }
            },
            PluginRequest::NetworkRequest { url } => {
                match &policy.permissions.network {
                    NetworkAccess::Disabled => {
                        return Err(SecurityError::PermissionDenied("network"));
                    },
                    NetworkAccess::AllowList(domains) => {
                        let domain = url.domain().ok_or(SecurityError::InvalidUrl)?;
                        if !domains.iter().any(|d| domain.ends_with(d)) {
                            return Err(SecurityError::DomainNotAllowed(domain.to_string()));
                        }
                    },
                    NetworkAccess::Enabled => {
                        // Allowed but logged
                        tracing::info!("Plugin {} making network request to {}", plugin_id, url);
                    }
                }
            },
            // ... other request types
        }
        
        Ok(())
    }
}
```

### IPC Security

All plugin communication goes through validated channels:

```rust
pub struct PluginChannel {
    sender: mpsc::Sender<PluginMessage>,
    receiver: mpsc::Receiver<PluginMessage>,
    message_validator: MessageValidator,
    rate_limiter: RateLimiter,
}

impl PluginChannel {
    pub async fn send(&self, message: PluginMessage) -> Result<(), ChannelError> {
        // Rate limiting to prevent DoS
        if !self.rate_limiter.allow() {
            return Err(ChannelError::RateLimitExceeded);
        }
        
        // Validate message structure
        self.message_validator.validate(&message)?;
        
        // Sanitize any string content
        let sanitized = self.sanitize_message(message)?;
        
        self.sender.send(sanitized).await
            .map_err(|_| ChannelError::ChannelClosed)
    }
    
    fn sanitize_message(&self, mut message: PluginMessage) -> Result<PluginMessage, SecurityError> {
        // Remove potential XSS payloads
        // Limit string lengths
        // Validate JSON structures
        // ... sanitization logic
        Ok(message)
    }
}
```

### Resource Quotas

Prevent plugins from consuming excessive resources:

```rust
pub struct ResourceLimiter {
    max_memory_bytes: u64,
    max_cpu_percent: f64,
    timeout: Duration,
    max_file_handles: u32,
}

impl ResourceLimiter {
    pub fn enforce(&self, plugin_process: &Child) -> Result<(), ResourceError> {
        #[cfg(target_os = "windows")]
        {
            use windows::Win32::System::JobObjects::*;
            
            // Create job object for process limits
            let job = CreateJobObjectW(None, None)?;
            
            // Set memory limit
            let mut mem_limit = JOBOBJECT_EXTENDED_LIMIT_INFORMATION::default();
            mem_limit.BasicLimitInformation.LimitFlags |= JOB_OBJECT_LIMIT_PROCESS_MEMORY;
            mem_limit.ProcessMemoryLimit = self.max_memory_bytes;
            
            SetInformationJobObject(
                job,
                JobObjectExtendedLimitInformation,
                &mut mem_limit as *mut _ as *mut _,
                size_of_val(&mem_limit) as u32,
            )?;
            
            // Assign process to job
            AssignProcessToJobObject(job, plugin_process.handle())?;
        }
        
        Ok(())
    }
}
```

### Plugin Verification

```rust
pub struct PluginVerifier {
    signature_validator: SignatureValidator,
    reputation_checker: ReputationChecker,
}

impl PluginVerifier {
    pub async fn verify_plugin(&self, plugin_path: &Path) -> Result<VerificationResult, VerificationError> {
        let manifest = self.load_manifest(plugin_path)?;
        
        // Check digital signature
        let signature_valid = self.signature_validator.verify(plugin_path)?;
        
        // Check against known malicious plugins
        let reputation = self.reputation_checker.check(&manifest.hash).await?;
        
        // Validate API compatibility
        let api_compatible = self.check_api_version(&manifest.api_version)?;
        
        // Static analysis for common vulnerabilities
        let security_scan = self.scan_for_vulnerabilities(plugin_path)?;
        
        Ok(VerificationResult {
            signature_valid,
            reputation_score: reputation.score,
            api_compatible,
            security_issues: security_scan.issues,
            recommended_action: self.determine_action(signature_valid, reputation, security_scan),
        })
    }
}
```

### Permission Levels

| Level | Description | Example Use Cases |
|-------|-------------|-------------------|
| **Minimal** | No filesystem, no network, timeline read-only | UI themes, keyboard shortcuts |
| **Standard** | Sandbox filesystem, timeline read/write | Effects, transitions, generators |
| **Elevated** | Project media access, limited network | Asset importers, cloud sync |
| **Full** | Unrestricted (user approval required) | Professional integrations |

## Consequences

### Positive

- **Security**: Strong isolation prevents most attack vectors
- **Stability**: Plugin crashes don't take down main app
- **User Trust**: Transparent permission model
- **Compliance**: Meets enterprise security requirements
- **Flexibility**: Granular permissions enable diverse plugins

### Negative

- **Performance Overhead**: IPC adds latency to plugin operations
- **Complexity**: Significant engineering effort for sandboxing
- **Plugin Development Friction**: Developers must work within constraints
- **False Positives**: Legitimate plugins may be blocked initially

### Mitigation Strategies

- Provide excellent plugin SDK with security best practices built-in
- Implement efficient IPC using shared memory where safe
- Create plugin testing tools that simulate security restrictions
- Build plugin certification program for verified developers
- Allow users to override restrictions for trusted plugins (with warnings)

## References

- Chrome Extension security model
- VS Code extension architecture
- WebAssembly sandboxing patterns
- Rust security guidelines
- OWASP plugin security checklist
- Adobe CEP security documentation
