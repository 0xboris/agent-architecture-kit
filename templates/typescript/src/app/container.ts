import { LoggingNoteStore } from '../domain/middleware/loggingNoteStore.ts';
import type { Clock, IdGenerator, NoteStore } from '../domain/ports.ts';
import { createRouter, type Handler } from '../sharedui/http.ts';
import type { Logger } from '../utilities/logger.ts';
import { wireNotes } from './wire-notes.ts';

export interface Dependencies {
  readonly noteStore: NoteStore;
  readonly clock: Clock;
  readonly ids: IdGenerator;
  readonly logger: Logger;
}

export function createApp(deps: Dependencies): { handle: Handler } {
  const wired: Dependencies = { ...deps, noteStore: new LoggingNoteStore(deps.noteStore, deps.logger) };
  const routes = [
    ...wireNotes(wired),
  ];
  return { handle: createRouter(routes, (error) => wired.logger.error('request failed', { error: String(error) })) };
}
