/**
 * Shared utility functions
 */

import { Timestamp, UUID } from '../types';

/**
 * Generate a new UUID (browser-compatible without external dependencies)
 */
export function generateUUID(): UUID {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  
  // Fallback for environments without crypto.randomUUID
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Get current timestamp in milliseconds
 */
export function now(): Timestamp {
  return Date.now();
}

/**
 * Format seconds into timecode string (HH:MM:SS.mmm)
 */
export function formatTimecode(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  const ms = Math.floor((seconds % 1) * 1000);

  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(3, '0')}`;
}

/**
 * Parse timecode string to seconds
 */
export function parseTimecode(timecode: string): number {
  const parts = timecode.split(':');
  if (parts.length !== 3) {
    throw new Error('Invalid timecode format. Expected HH:MM:SS.mmm');
  }

  const [hours, minutes, rest] = parts;
  const [seconds, ms] = rest.split('.');

  return (
    parseInt(hours, 10) * 3600 +
    parseInt(minutes, 10) * 60 +
    parseInt(seconds, 10) +
    (ms ? parseInt(ms, 10) / 1000 : 0)
  );
}

/**
 * Format bytes to human-readable string
 */
export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 B';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

/**
 * Clamp a value between min and max
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Linear interpolation
 */
export function lerp(start: number, end: number, t: number): number {
  return start + (end - start) * clamp(t, 0, 1);
}

/**
 * Deep clone an object
 */
export function deepClone<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Debounce a function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle a function
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false;

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Check if a file extension is supported
 */
export function isVideoExtension(ext: string): boolean {
  const normalized = ext.toLowerCase();
  return [
    '.mp4', '.mov', '.avi', '.mkv', '.webm',
    '.m4v', '.mpeg', '.mpg', '.wmv', '.flv'
  ].includes(normalized);
}

export function isImageExtension(ext: string): boolean {
  const normalized = ext.toLowerCase();
  return [
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    '.tiff', '.tif', '.webp', '.svg', '.heic', '.heif'
  ].includes(normalized);
}

export function isAudioExtension(ext: string): boolean {
  const normalized = ext.toLowerCase();
  return [
    '.mp3', '.wav', '.aac', '.flac', '.ogg',
    '.m4a', '.wma', '.aiff'
  ].includes(normalized);
}

/**
 * Calculate progress percentage
 */
export function calculateProgress(current: number, total: number): number {
  if (total === 0) return 0;
  return clamp((current / total) * 100, 0, 100);
}

/**
 * Sleep for a specified duration
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry a function with exponential backoff
 */
export async function retry<T>(
  fn: () => Promise<T>,
  maxAttempts = 3,
  baseDelay = 1000
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      if (attempt < maxAttempts) {
        const delay = baseDelay * Math.pow(2, attempt - 1);
        await sleep(delay);
      }
    }
  }

  throw lastError || new Error('Retry failed');
}

/**
 * Group array items by a key
 */
export function groupBy<T>(array: T[], keyFn: (item: T) => string): Record<string, T[]> {
  return array.reduce((groups, item) => {
    const key = keyFn(item);
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);
    return groups;
  }, {} as Record<string, T[]>);
}

/**
 * Partition array based on predicate
 */
export function partition<T>(array: T[], predicate: (item: T) => boolean): [T[], T[]] {
  const truthy: T[] = [];
  const falsy: T[] = [];

  for (const item of array) {
    if (predicate(item)) {
      truthy.push(item);
    } else {
      falsy.push(item);
    }
  }

  return [truthy, falsy];
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number, ellipsis = '...'): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - ellipsis.length) + ellipsis;
}

/**
 * Sanitize filename
 */
export function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[<>:"/\\|?*]/g, '')
    .replace(/\s+/g, '_')
    .toLowerCase();
}

/**
 * Create a promise that resolves after a timeout
 */
export function timeout(ms: number, message = 'Operation timed out'): Promise<never> {
  return new Promise((_, reject) => {
    setTimeout(() => reject(new Error(message)), ms);
  });
}

/**
 * Race a promise against a timeout
 */
export function withTimeout<T>(promise: Promise<T>, ms: number, message?: string): Promise<T> {
  return Promise.race([promise, timeout(ms, message)]);
}

/**
 * Check if running on Windows
 */
export function isWindows(): boolean {
  return typeof navigator !== 'undefined' && navigator.platform.includes('Win');
}

/**
 * Check if running on macOS
 */
export function isMacOS(): boolean {
  return typeof navigator !== 'undefined' && navigator.platform.includes('Mac');
}

/**
 * Check if running on Linux
 */
export function isLinux(): boolean {
  return typeof navigator !== 'undefined' && navigator.platform.includes('Linux');
}

/**
 * Get file extension from path
 */
export function getExtension(path: string): string {
  const lastDot = path.lastIndexOf('.');
  if (lastDot === -1) return '';
  return path.slice(lastDot).toLowerCase();
}

/**
 * Get filename without extension
 */
export function getBasename(path: string): string {
  const basename = path.split(/[\\/]/).pop() || '';
  const lastDot = basename.lastIndexOf('.');
  if (lastDot === -1) return basename;
  return basename.slice(0, lastDot);
}

/**
 * Normalize path separators
 */
export function normalizePath(path: string): string {
  return path.replace(/\\/g, '/');
}

/**
 * Join path segments
 */
export function joinPath(...segments: string[]): string {
  return segments
    .map(segment => segment.replace(/^[\\/]+|[\\/]+$/g, ''))
    .filter(segment => segment.length > 0)
    .join('/');
}
