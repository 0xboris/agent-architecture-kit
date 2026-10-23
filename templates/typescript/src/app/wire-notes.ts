import { notesRoutes } from '../features/notes/ui/notesRoutes.ts';
import { createNote } from '../features/notes/usecases/createNote.ts';
import { listNotes } from '../features/notes/usecases/listNotes.ts';
import type { Route } from '../sharedui/http.ts';
import type { Dependencies } from './container.ts';

export function wireNotes(deps: Dependencies): Route[] {
  const store = deps.noteStore;
  return notesRoutes({
    createNote: (rawTitle) => createNote({ store, clock: deps.clock, ids: deps.ids }, rawTitle),
    listNotes: () => listNotes({ store }),
    logger: deps.logger,
  });
}
