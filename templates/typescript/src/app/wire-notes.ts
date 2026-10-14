import { notesRoutes } from '../features/notes/ui/notesRoutes.ts';
import { CreateNote } from '../features/notes/usecases/createNote.ts';
import { ListNotes } from '../features/notes/usecases/listNotes.ts';
import type { Route } from '../sharedui/http.ts';
import type { Dependencies } from './container.ts';

export function wireNotes(deps: Dependencies): Route[] {
  return notesRoutes({
    createNote: new CreateNote({ store: deps.noteStore, clock: deps.clock, ids: deps.ids }),
    listNotes: new ListNotes({ store: deps.noteStore }),
    logger: deps.logger,
  });
}
