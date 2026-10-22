import { maxTitleLength, type Note, type NoteTitleError } from '../../../domain/note.ts';
import { readJson, sendError, sendJson, type Route } from '../../../sharedui/http.ts';
import type { Logger } from '../../../utilities/logger.ts';
import type { createNote } from '../usecases/createNote.ts';
import type { listNotes } from '../usecases/listNotes.ts';

interface NoteResponse {
  readonly id: string;
  readonly title: string;
  readonly createdAt: string;
}

const titleErrors: Record<NoteTitleError, { readonly code: string; readonly message: string }> = {
  empty: { code: 'title_empty', message: 'Enter a title.' },
  tooLong: { code: 'title_too_long', message: `Use at most ${maxTitleLength} characters.` },
};

function toResponse(note: Note): NoteResponse {
  return { id: note.id, title: note.title, createdAt: note.createdAt.toISOString() };
}

function parseCreateRequest(body: unknown): { title: string } | undefined {
  if (typeof body === 'object' && body !== null && 'title' in body && typeof body.title === 'string') {
    return { title: body.title };
  }
  return undefined;
}

export function notesRoutes(deps: {
  createNote: (rawTitle: string) => ReturnType<typeof createNote>;
  listNotes: () => ReturnType<typeof listNotes>;
  logger: Logger;
}): Route[] {
  return [
    {
      method: 'GET',
      path: '/notes',
      handle: async (_request, response) => {
        try {
          const notes = await deps.listNotes();
          sendJson(response, 200, notes.map(toResponse));
        } catch (error) {
          deps.logger.error('list notes failed', { error: String(error) });
          sendError(response, { status: 500, code: 'notes_unavailable', message: 'The notes could not be loaded.' });
        }
      },
    },
    {
      method: 'POST',
      path: '/notes',
      handle: async (request, response) => {
        let body: { title: string } | undefined;
        try {
          body = parseCreateRequest(await readJson(request));
        } catch {
          body = undefined;
        }
        if (body === undefined) {
          sendError(response, { status: 400, code: 'invalid_request', message: 'Send a JSON object with a title.' });
          return;
        }
        try {
          const result = await deps.createNote(body.title);
          if (result.ok) {
            sendJson(response, 201, toResponse(result.value));
          } else {
            sendError(response, { status: 422, ...titleErrors[result.error] });
          }
        } catch (error) {
          deps.logger.error('create note failed', { error: String(error) });
          sendError(response, { status: 500, code: 'note_not_saved', message: 'The note could not be saved.' });
        }
      },
    },
  ];
}
