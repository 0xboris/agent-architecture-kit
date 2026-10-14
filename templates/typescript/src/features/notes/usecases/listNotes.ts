import type { Note } from '../../../domain/note.ts';
import { newestFirst } from '../../../domain/ordering.ts';
import type { NoteStore } from '../../../domain/ports.ts';

export class ListNotes {
  readonly #store: NoteStore;

  constructor(deps: { store: NoteStore }) {
    this.#store = deps.store;
  }

  async run(): Promise<Note[]> {
    return newestFirst(await this.#store.allNotes());
  }
}
