/** The logging interface. The platform adapter implements it, and tests use RecordingLogger. */
export interface Logger {
  info(message: string, metadata?: Record<string, string>): void;
  error(message: string, metadata?: Record<string, string>): void;
}
