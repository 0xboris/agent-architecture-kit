import type { Logger } from '../../utilities/logger.ts';
import type { Note } from '../note.ts';
import type { NoteStore } from '../ports.ts';

/**
 * Middleware: wraps any NoteStore and logs each save. The composition root
 * applies it once to the real store, so every slice gets it.
 */
export class LoggingNoteStore implements NoteStore {
  readonly #base: NoteStore;
  readonly #logger: Logger;

  constructor(base: NoteStore, logger: Logger) {
    this.#base = base;
    this.#logger = logger;
  }

  allNotes(): Promise<Note[]> {
    return this.#base.allNotes();
  }

  async save(note: Note): Promise<void> {
    await this.#base.save(note);
    this.#logger.info('note saved', { id: note.id });
  }
}
