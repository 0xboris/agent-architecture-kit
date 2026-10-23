export interface Logger {
  info(message: string, metadata?: Record<string, string>): void;
  error(message: string, metadata?: Record<string, string>): void;
}
