/**
 * Shared type definitions for VID-ED
 * These types are used across the renderer, Tauri backend, and AI runtime
 */

// ============================================================================
// Core Types
// ============================================================================

export type UUID = string;

export type Timestamp = number;

export interface Identifiable {
  id: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

// ============================================================================
// Timeline Types
// ============================================================================

export type TrackType = 'video' | 'audio' | 'text' | 'effect' | 'adjustment';

export interface TimelineClip extends Identifiable {
  type: 'clip';
  trackId: UUID;
  sourceId: UUID;
  startTime: number; // In seconds (timeline position)
  duration: number; // In seconds
  sourceInPoint: number; // In seconds (source media position)
  sourceOutPoint: number; // In seconds
  name: string;
  metadata?: Record<string, unknown>;
}

export interface TimelineTransition extends Identifiable {
  type: 'transition';
  trackId: UUID;
  clipAId: UUID;
  clipBId: UUID;
  transitionType: string;
  duration: number;
  parameters?: Record<string, unknown>;
}

export interface TimelineEffect extends Identifiable {
  type: 'effect';
  trackId: UUID;
  clipId: UUID;
  effectType: string;
  startTime: number;
  duration: number;
  parameters?: Record<string, unknown>;
}

export interface TimelineTrack extends Identifiable {
  name: string;
  type: TrackType;
  clips: TimelineClip[];
  transitions: TimelineTransition[];
  effects: TimelineEffect[];
  muted: boolean;
  locked: boolean;
  volume?: number;
  opacity?: number;
}

export interface TimelineMarker extends Identifiable {
  time: number;
  label: string;
  color: string;
  notes?: string;
}

export interface TimelineState extends Identifiable {
  name: string;
  width: number;
  height: number;
  frameRate: number;
  totalDuration: number;
  tracks: TimelineTrack[];
  markers: TimelineMarker[];
  version: number;
}

// ============================================================================
// Media Types
// ============================================================================

export type MediaType = 'video' | 'image' | 'audio' | 'sequence';

export interface MediaSource extends Identifiable {
  type: MediaType;
  path: string;
  name: string;
  duration?: number;
  width?: number;
  height?: number;
  frameRate?: number;
  hasAudio: boolean;
  thumbnailPath?: string;
  metadata: MediaMetadata;
}

export interface MediaMetadata {
  codec?: string;
  bitRate?: number;
  sampleRate?: number;
  channels?: number;
  format?: string;
  fileSize: number;
  createdDate?: Timestamp;
  modifiedDate?: Timestamp;
  tags?: string[];
  description?: string;
}

// ============================================================================
// AI Agent Types
// ============================================================================

export type AgentName =
  | 'creative-director'
  | 'task-planner'
  | 'scheduler'
  | 'timeline'
  | 'story'
  | 'caption'
  | 'research'
  | 'brand'
  | 'publishing'
  | 'motion'
  | 'vfx'
  | 'audio'
  | 'voice'
  | 'color'
  | 'review'
  | 'hardware-detection'
  | 'model-router'
  | 'memory-manager';

export interface AgentMessage {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  timestamp?: Timestamp;
  agentName?: AgentName;
  metadata?: Record<string, unknown>;
}

export interface AgentTask {
  id: UUID;
  name: string;
  description: string;
  agentName: AgentName;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0-100
  result?: unknown;
  error?: string;
  startedAt?: Timestamp;
  completedAt?: Timestamp;
}

export interface CreativeBrief {
  id: UUID;
  title: string;
  objective: string;
  targetAudience: string;
  keyMessages: string[];
  toneAndStyle: string;
  references?: string[];
  constraints?: string[];
  deliverables: string[];
  createdAt: Timestamp;
}

export interface StyleBlueprint {
  id: UUID;
  name: string;
  pacing: 'slow' | 'medium' | 'fast' | 'dynamic';
  transitionStyle: string;
  captionStyle: CaptionStyle;
  colorPalette: ColorPalette;
  typography: Typography;
  editingPatterns: EditingPattern[];
}

export interface CaptionStyle {
  fontFamily: string;
  fontSize: number;
  color: string;
  backgroundColor?: string;
  position: 'bottom' | 'top' | 'center';
  animation?: string;
}

export interface ColorPalette {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
}

export interface Typography {
  headingFont: string;
  bodyFont: string;
  scale: number;
}

export interface EditingPattern {
  name: string;
  description: string;
  shotDuration: number;
  cutFrequency: number;
  movementIntensity: number;
}

// ============================================================================
// Hardware Types
// ============================================================================

export interface HardwareProfile {
  cpu: CPUInfo;
  gpu: GPUInfo[];
  ram: MemoryInfo;
  vram: MemoryInfo[];
  storage: StorageInfo[];
  capabilities: HardwareCapabilities;
}

export interface CPUInfo {
  model: string;
  cores: number;
  threads: number;
  baseSpeed: number;
  maxSpeed: number;
  architecture: string;
  avxSupport: boolean;
  avx2Support: boolean;
  avx512Support: boolean;
}

export interface GPUInfo {
  name: string;
  vendor: 'nvidia' | 'amd' | 'intel' | 'apple' | 'unknown';
  vram: number;
  cudaCores?: number;
  computeCapability?: string;
  directMLSupport: boolean;
  metalSupport: boolean;
  openCLSupport: boolean;
}

export interface MemoryInfo {
  total: number;
  available: number;
  used: number;
}

export interface StorageInfo {
  path: string;
  total: number;
  free: number;
  type: 'ssd' | 'hdd' | 'nvme' | 'unknown';
  readSpeed?: number;
  writeSpeed?: number;
}

export interface HardwareCapabilities {
  cudaAvailable: boolean;
  directMLAvailable: boolean;
  metalAvailable: boolean;
  openCLAvailable: boolean;
  recommendedBatchSize: number;
  recommendedModelSize: 'tiny' | 'small' | 'medium' | 'large' | 'xlarge';
  canRunLocalAI: boolean;
  gpuAccelerationLevel: 'none' | 'basic' | 'advanced' | 'full';
}

// ============================================================================
// Plugin Types
// ============================================================================

export interface PluginManifest {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  homepage?: string;
  license: string;
  minVidEdVersion: string;
  permissions: PluginPermission[];
  entryPoint: string;
  icon?: string;
}

export type PluginPermission =
  | 'timeline:read'
  | 'timeline:write'
  | 'media:read'
  | 'media:write'
  | 'ai:access'
  | 'render:access'
  | 'filesystem:sandbox'
  | 'network:external';

export interface PluginContext {
  timeline: TimelineAPI;
  media: MediaAPI;
  ai: AIAPI;
  render: RenderAPI;
  storage: StorageAPI;
}

export interface TimelineAPI {
  getCurrentTimeline: () => Promise<TimelineState>;
  updateTimeline: (timeline: Partial<TimelineState>) => Promise<void>;
  addClip: (clip: Omit<TimelineClip, 'id' | 'createdAt' | 'updatedAt'>) => Promise<UUID>;
  removeClip: (clipId: UUID) => Promise<void>;
  subscribe: (callback: (timeline: TimelineState) => void) => () => void;
}

export interface MediaAPI {
  importMedia: (paths: string[]) => Promise<MediaSource[]>;
  getMedia: (id: UUID) => Promise<MediaSource | null>;
  getAllMedia: () => Promise<MediaSource[]>;
  deleteMedia: (id: UUID) => Promise<void>;
}

export interface AIAPI {
  sendMessage: (message: string, context?: Record<string, unknown>) => Promise<string>;
  runTask: (agentName: AgentName, task: string, params?: Record<string, unknown>) => Promise<AgentTask>;
  getCreativeBrief: () => Promise<CreativeBrief | null>;
  getStyleBlueprint: () => Promise<StyleBlueprint | null>;
}

export interface RenderAPI {
  preview: (timeline: TimelineState, time: number) => Promise<string>;
  export: (timeline: TimelineState, options: ExportOptions) => Promise<string>;
  cancelExport: (jobId: UUID) => Promise<void>;
}

export interface StorageAPI {
  read: (path: string) => Promise<string>;
  write: (path: string, data: string) => Promise<void>;
  exists: (path: string) => Promise<boolean>;
  list: (directory: string) => Promise<string[]>;
}

export interface ExportOptions {
  format: 'mp4' | 'mov' | 'webm' | 'gif';
  resolution: '1080p' | '720p' | '4k' | 'custom';
  customWidth?: number;
  customHeight?: number;
  frameRate?: number;
  quality: 'low' | 'medium' | 'high' | 'ultra';
  outputPath: string;
}

// ============================================================================
// Event Types
// ============================================================================

export type EventType =
  | 'timeline:changed'
  | 'timeline:playback'
  | 'media:imported'
  | 'media:deleted'
  | 'agent:message'
  | 'agent:task-started'
  | 'agent:task-completed'
  | 'agent:task-failed'
  | 'render:started'
  | 'render:progress'
  | 'render:completed'
  | 'render:failed'
  | 'hardware:detected'
  | 'plugin:loaded'
  | 'plugin:unloaded'
  | 'app:ready'
  | 'app:quit';

export interface AppEvent {
  type: EventType;
  payload: unknown;
  timestamp: Timestamp;
  source: string;
}

// ============================================================================
// Settings Types
// ============================================================================

export interface AppSettings {
  general: GeneralSettings;
  editor: EditorSettings;
  ai: AISettings;
  render: RenderSettings;
  shortcuts: ShortcutSettings;
}

export interface GeneralSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  autoSave: boolean;
  autoSaveInterval: number;
  projectsDirectory: string;
  cacheDirectory: string;
}

export interface EditorSettings {
  defaultResolution: string;
  defaultFrameRate: number;
  snapToGrid: boolean;
  gridSize: number;
  showWaveforms: boolean;
  proxyEnabled: boolean;
  proxyResolution: string;
}

export interface AISettings {
  localAIPriority: boolean;
  preferredModels: Record<AgentName, string>;
  cloudAIFallback: boolean;
  enableResearch: boolean;
  enableMemory: boolean;
}

export interface RenderSettings {
  defaultFormat: string;
  defaultQuality: string;
  hardwareAcceleration: boolean;
  parallelEncoding: boolean;
  maxConcurrentJobs: number;
}

export interface ShortcutSettings {
  [key: string]: string;
}

// ============================================================================
// Memory Types
// ============================================================================

export interface MemoryItem extends Identifiable {
  type: 'brand' | 'creator' | 'project' | 'preference' | 'pattern';
  content: Record<string, unknown>;
  embeddings?: number[];
  tags: string[];
  importance: number;
  lastAccessed: Timestamp;
  accessCount: number;
}

export interface BrandMemory {
  brandName: string;
  logoPath?: string;
  colorPalette: ColorPalette;
  typography: Typography;
  voiceAndTone: string;
  doNotUse: string[];
  pastProjects: UUID[];
}

export interface CreatorMemory {
  creatorName: string;
  stylePreferences: StyleBlueprint;
  preferredWorkflows: string[];
  favoriteEffects: string[];
  publishingPlatforms: string[];
  analyticsData?: Record<string, unknown>;
}
