import { randomUUID } from 'node:crypto';
import type { Clock, IdGenerator } from '../../domain/ports.ts';
import type { Logger } from '../../utilities/logger.ts';

export class SystemClock implements Clock {
  now(): Date {
    return new Date();
  }
}

export class RandomIds implements IdGenerator {
  newId(): string {
    return randomUUID();
  }
}

/** Writes one JSON line per log entry to standard error. */
export class ConsoleLogger implements Logger {
  info(message: string, metadata: Record<string, string> = {}): void {
    console.error(JSON.stringify({ level: 'info', message, ...metadata }));
  }

  error(message: string, metadata: Record<string, string> = {}): void {
    console.error(JSON.stringify({ level: 'error', message, ...metadata }));
  }
}
