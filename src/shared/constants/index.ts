/**
 * Application Constants
 */

// ============================================================================
// Version Information
// ============================================================================

export const APP_VERSION = '0.1.0';
export const MIN_PLUGIN_API_VERSION = '1.0.0';

// ============================================================================
// Default Values
// ============================================================================

export const DEFAULT_TIMELINE = {
  width: 1920,
  height: 1080,
  frameRate: 30,
  totalDuration: 60,
};

export const DEFAULT_SETTINGS = {
  general: {
    theme: 'dark' as const,
    language: 'en',
    autoSave: true,
    autoSaveInterval: 300, // 5 minutes
    projectsDirectory: '',
    cacheDirectory: '',
  },
  editor: {
    defaultResolution: '1080p',
    defaultFrameRate: 30,
    snapToGrid: true,
    gridSize: 1,
    showWaveforms: true,
    proxyEnabled: false,
    proxyResolution: '720p',
  },
  ai: {
    localAIPriority: true,
    preferredModels: {} as Record<string, string>,
    cloudAIFallback: false,
    enableResearch: true,
    enableMemory: true,
  },
  render: {
    defaultFormat: 'mp4',
    defaultQuality: 'high',
    hardwareAcceleration: true,
    parallelEncoding: true,
    maxConcurrentJobs: 2,
  },
};

// ============================================================================
// File Extensions
// ============================================================================

export const VIDEO_EXTENSIONS = [
  '.mp4',
  '.mov',
  '.avi',
  '.mkv',
  '.webm',
  '.m4v',
  '.mpeg',
  '.mpg',
  '.wmv',
  '.flv',
];

export const IMAGE_EXTENSIONS = [
  '.jpg',
  '.jpeg',
  '.png',
  '.gif',
  '.bmp',
  '.tiff',
  '.tif',
  '.webp',
  '.svg',
  '.heic',
  '.heif',
];

export const AUDIO_EXTENSIONS = [
  '.mp3',
  '.wav',
  '.aac',
  '.flac',
  '.ogg',
  '.m4a',
  '.wma',
  '.aiff',
];

export const SEQUENCE_EXTENSIONS = ['.dpx', '.exr', '.png', '.jpg', '.tiff'];

// ============================================================================
// Timeline Constraints
// ============================================================================

export const MIN_CLIP_DURATION = 0.1; // seconds
export const MAX_TRACKS = 100;
export const MAX_CLIPS_PER_TRACK = 10000;
export const SUPPORTED_FRAME_RATES = [23.976, 24, 25, 29.97, 30, 50, 59.94, 60];
export const SUPPORTED_RESOLUTIONS = [
  { name: '4K UHD', width: 3840, height: 2160 },
  { name: '1080p', width: 1920, height: 1080 },
  { name: '720p', width: 1280, height: 720 },
  { name: 'Vertical 9:16', width: 1080, height: 1920 },
  { name: 'Square 1:1', width: 1080, height: 1080 },
];

// ============================================================================
// AI Model Defaults
// ============================================================================

export const MODEL_SIZES = {
  tiny: { maxVRAM: 2, description: '< 1GB VRAM' },
  small: { maxVRAM: 4, description: '1-2GB VRAM' },
  medium: { maxVRAM: 8, description: '2-4GB VRAM' },
  large: { maxVRAM: 16, description: '4-8GB VRAM' },
  xlarge: { maxVRAM: 24, description: '> 8GB VRAM' },
} as const;

export const AGENT_DEFAULTS = {
  'creative-director': {
    modelSize: 'medium' as const,
    priority: 'high',
  },
  'task-planner': {
    modelSize: 'small' as const,
    priority: 'high',
  },
  timeline: {
    modelSize: 'small' as const,
    priority: 'medium',
  },
  story: {
    modelSize: 'medium' as const,
    priority: 'medium',
  },
  caption: {
    modelSize: 'tiny' as const,
    priority: 'low',
  },
  research: {
    modelSize: 'medium' as const,
    priority: 'low',
  },
  motion: {
    modelSize: 'small' as const,
    priority: 'medium',
  },
  vfx: {
    modelSize: 'small' as const,
    priority: 'medium',
  },
  audio: {
    modelSize: 'tiny' as const,
    priority: 'low',
  },
  voice: {
    modelSize: 'tiny' as const,
    priority: 'low',
  },
  color: {
    modelSize: 'tiny' as const,
    priority: 'low',
  },
  review: {
    modelSize: 'small' as const,
    priority: 'medium',
  },
} as const;

// ============================================================================
// Performance Thresholds
// ============================================================================

export const PERFORMANCE_THRESHOLDS = {
  lowRAM: 8 * 1024, // 8GB
  recommendedRAM: 16 * 1024, // 16GB
  lowVRAM: 4 * 1024, // 4GB
  recommendedVRAM: 8 * 1024, // 8GB
  lowDiskSpace: 10 * 1024, // 10GB
  minimumFreeDisk: 5 * 1024, // 5GB
};

// ============================================================================
// Keyboard Shortcuts (Defaults)
// ============================================================================

export const DEFAULT_SHORTCUTS = {
  // Playback
  'playback.toggle': 'Space',
  'playback.play': 'L',
  'playback.pause': 'K',
  'playback.rewind': 'J',
  'playback.frameForward': 'Right',
  'playback.frameBackward': 'Left',
  
  // Editing
  'edit.cut': 'Ctrl+K',
  'edit.delete': 'Delete',
  'edit.rippleDelete': 'Shift+Delete',
  'edit.undo': 'Ctrl+Z',
  'edit.redo': 'Ctrl+Y',
  'edit.copy': 'Ctrl+C',
  'edit.paste': 'Ctrl+V',
  'edit.duplicate': 'Ctrl+D',
  
  // Timeline
  'timeline.zoomIn': 'Ctrl+=',
  'timeline.zoomOut': 'Ctrl+-',
  'timeline.fitToScreen': 'Shift+0',
  'timeline.selectAll': 'Ctrl+A',
  
  // Tools
  'tool.select': 'V',
  'tool.trim': 'T',
  'tool.slip': 'S',
  'tool.slide': 'D',
  'tool.pen': 'P',
  'tool.text': 'Ctrl+T',
  
  // Navigation
  'navigation.projectPanel': 'Ctrl+1',
  'navigation.timelinePanel': 'Ctrl+2',
  'navigation.previewPanel': 'Ctrl+3',
  'navigation.aiPanel': 'Ctrl+4',
  
  // Misc
  'app.save': 'Ctrl+S',
  'app.export': 'Ctrl+E',
  'app.preferences': 'Ctrl+,',
  'app.commandPalette': 'Ctrl+Shift+P',
  'app.quit': 'Ctrl+Q',
};

// ============================================================================
// Color Palette (Design System)
// ============================================================================

export const COLORS = {
  // Light Theme
  light: {
    background: '#FFFFFF',
    surface: '#F8F9FA',
    surfaceElevated: '#FFFFFF',
    border: '#E9ECEF',
    text: '#212529',
    textSecondary: '#6C757D',
    textMuted: '#ADB5BD',
    primary: '#0066FF',
    primaryHover: '#0052CC',
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
  },
  // Dark Theme
  dark: {
    background: '#0D1117',
    surface: '#161B22',
    surfaceElevated: '#21262D',
    border: '#30363D',
    text: '#F0F6FC',
    textSecondary: '#8B949E',
    textMuted: '#484F58',
    primary: '#58A6FF',
    primaryHover: '#79C0FF',
    success: '#3FB950',
    warning: '#D29922',
    error: '#F85149',
    info: '#58A6FF',
  },
};

// ============================================================================
// Track Colors
// ============================================================================

export const TRACK_COLORS = {
  video: '#3B82F6',
  audio: '#10B981',
  text: '#F59E0B',
  effect: '#8B5CF6',
  adjustment: '#EC4899',
};

// ============================================================================
// API Endpoints (for cloud features)
// ============================================================================

export const API_ENDPOINTS = {
  cloudRender: '/api/v1/render',
  cloudAI: '/api/v1/ai',
  modelDownload: '/api/v1/models',
  pluginRegistry: '/api/v1/plugins',
  telemetry: '/api/v1/telemetry',
} as const;

// ============================================================================
// Feature Flags
// ============================================================================

export const FEATURE_FLAGS = {
  enableCloudRender: false,
  enableCloudAI: false,
  enableResearch: true,
  enablePlugins: true,
  enableTelemetry: false,
  enableBetaFeatures: false,
} as const;

// ============================================================================
// Error Codes
// ============================================================================

export const ERROR_CODES = {
  // General
  UNKNOWN_ERROR: 'ERR_UNKNOWN',
  INVALID_ARGUMENT: 'ERR_INVALID_ARGUMENT',
  OPERATION_CANCELLED: 'ERR_OPERATION_CANCELLED',
  
  // File System
  FILE_NOT_FOUND: 'ERR_FILE_NOT_FOUND',
  PERMISSION_DENIED: 'ERR_PERMISSION_DENIED',
  DISK_FULL: 'ERR_DISK_FULL',
  
  // Timeline
  TIMELINE_INVALID: 'ERR_TIMELINE_INVALID',
  CLIP_NOT_FOUND: 'ERR_CLIP_NOT_FOUND',
  TRACK_NOT_FOUND: 'ERR_TRACK_NOT_FOUND',
  INVALID_EDIT: 'ERR_INVALID_EDIT',
  
  // Rendering
  RENDER_FAILED: 'ERR_RENDER_FAILED',
  ENCODER_NOT_FOUND: 'ERR_ENCODER_NOT_FOUND',
  RENDER_CANCELLED: 'ERR_RENDER_CANCELLED',
  
  // AI
  AI_MODEL_NOT_FOUND: 'ERR_AI_MODEL_NOT_FOUND',
  AI_INFERENCE_FAILED: 'ERR_AI_INFERENCE_FAILED',
  AI_TIMEOUT: 'ERR_AI_TIMEOUT',
  AI_OUT_OF_MEMORY: 'ERR_AI_OOM',
  
  // Hardware
  HARDWARE_UNSUPPORTED: 'ERR_HARDWARE_UNSUPPORTED',
  GPU_NOT_FOUND: 'ERR_GPU_NOT_FOUND',
  INSUFFICIENT_VRAM: 'ERR_INSUFFICIENT_VRAM',
  
  // Plugin
  PLUGIN_LOAD_FAILED: 'ERR_PLUGIN_LOAD_FAILED',
  PLUGIN_PERMISSION_DENIED: 'ERR_PLUGIN_PERMISSION_DENIED',
  PLUGIN_INCOMPATIBLE: 'ERR_PLUGIN_INCOMPATIBLE',
} as const;

// ============================================================================
// IPC Channels (Tauri)
// ============================================================================

export const IPC_CHANNELS = {
  // Core
  'app:ready': 'app:ready',
  'app:quit': 'app:quit',
  'app:getVersion': 'app:getVersion',
  
  // File System
  'fs:read': 'fs:read',
  'fs:write': 'fs:write',
  'fs:delete': 'fs:delete',
  'fs:exists': 'fs:exists',
  'fs:list': 'fs:list',
  'fs:import': 'fs:import',
  
  // Timeline
  'timeline:get': 'timeline:get',
  'timeline:update': 'timeline:update',
  'timeline:export': 'timeline:export',
  'timeline:import': 'timeline:import',
  
  // Media
  'media:import': 'media:import',
  'media:get': 'media:get',
  'media:list': 'media:list',
  'media:delete': 'media:delete',
  'media:analyze': 'media:analyze',
  'media:thumbnail': 'media:thumbnail',
  
  // AI
  'ai:chat': 'ai:chat',
  'ai:task': 'ai:task',
  'ai:cancel': 'ai:cancel',
  'ai:models:list': 'ai:models:list',
  'ai:models:download': 'ai:models:download',
  'ai:models:delete': 'ai:models:delete',
  
  // Render
  'render:preview': 'render:preview',
  'render:export': 'render:export',
  'render:cancel': 'render:cancel',
  'render:status': 'render:status',
  
  // Hardware
  'hardware:detect': 'hardware:detect',
  'hardware:profile': 'hardware:profile',
  
  // Memory
  'memory:save': 'memory:save',
  'memory:load': 'memory:load',
  'memory:search': 'memory:search',
  'memory:delete': 'memory:delete',
  
  // Plugins
  'plugins:list': 'plugins:list',
  'plugins:load': 'plugins:load',
  'plugins:unload': 'plugins:unload',
  'plugins:invoke': 'plugins:invoke',
  
  // Settings
  'settings:get': 'settings:get',
  'settings:set': 'settings:set',
  'settings:reset': 'settings:reset',
} as const;
