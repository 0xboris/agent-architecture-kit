import type { Note } from '../../../domain/note.ts';
import { newestFirst } from '../../../domain/ordering.ts';
import type { NoteStore } from '../../../domain/ports.ts';

export async function listNotes(deps: { store: NoteStore }): Promise<Note[]> {
  return newestFirst(await deps.store.allNotes());
}
