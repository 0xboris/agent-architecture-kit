import { parseNoteTitle, type Note, type NoteTitleError } from '../../../domain/note.ts';
import type { Clock, IdGenerator, NoteStore } from '../../../domain/ports.ts';
import type { Result } from '../../../utilities/result.ts';

/** Creates a note from what the user typed. Orchestration only: the title rules live in the domain. */
export class CreateNote {
  readonly #store: NoteStore;
  readonly #clock: Clock;
  readonly #ids: IdGenerator;

  constructor(deps: { store: NoteStore; clock: Clock; ids: IdGenerator }) {
    this.#store = deps.store;
    this.#clock = deps.clock;
    this.#ids = deps.ids;
  }

  async run(rawTitle: string): Promise<Result<Note, NoteTitleError>> {
    const title = parseNoteTitle(rawTitle);
    if (!title.ok) return title;
    const note: Note = { id: this.#ids.newId(), title: title.value, createdAt: this.#clock.now() };
    await this.#store.save(note);
    return { ok: true, value: note };
  }
}
