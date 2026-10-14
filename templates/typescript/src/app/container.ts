import { LoggingNoteStore } from '../domain/middleware/loggingNoteStore.ts';
import type { Clock, IdGenerator, NoteStore } from '../domain/ports.ts';
import { createRouter, type Handler } from '../sharedui/http.ts';
import type { Logger } from '../utilities/logger.ts';
import { wireNotes } from './wire-notes.ts';
// scaffold:imports

/**
 * The composition root. It applies middleware and wires each slice in a
 * wire-<slice>.ts file. It holds straight-line wiring only: no control flow
 * and no feature code.
 */

/** The adapters that the service runs with. liveDependencies creates the real ones; the composition test passes fakes. */
export interface Dependencies {
  readonly noteStore: NoteStore;
  readonly clock: Clock;
  readonly ids: IdGenerator;
  readonly logger: Logger;
}

export function createApp(deps: Dependencies): { handle: Handler } {
  // Mandatory middleware: applied once here, so no slice receives the bare store.
  const wired: Dependencies = { ...deps, noteStore: new LoggingNoteStore(deps.noteStore, deps.logger) };
  const routes = [
    ...wireNotes(wired),
    // scaffold:routes
  ];
  return { handle: createRouter(routes, (error) => wired.logger.error('request failed', { error: String(error) })) };
}
