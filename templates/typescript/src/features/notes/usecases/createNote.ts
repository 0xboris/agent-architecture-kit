import { parseNoteTitle, type Note, type NoteTitleError } from '../../../domain/note.ts';
import type { Clock, IdGenerator, NoteStore } from '../../../domain/ports.ts';
import type { Result } from '../../../utilities/result.ts';

export async function createNote(
  deps: { store: NoteStore; clock: Clock; ids: IdGenerator },
  rawTitle: string,
): Promise<Result<Note, NoteTitleError>> {
  const title = parseNoteTitle(rawTitle);
  if (!title.ok) return title;
  const note: Note = { id: deps.ids.newId(), title: title.value, createdAt: deps.clock.now() };
  await deps.store.save(note);
  return { ok: true, value: note };
}
