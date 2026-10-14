import { maxTitleLength, type Note } from '../../../domain/note.ts';
import { readJson, sendError, sendJson, type Route } from '../../../sharedui/http.ts';
import type { Logger } from '../../../utilities/logger.ts';
import type { CreateNote } from '../usecases/createNote.ts';
import type { ListNotes } from '../usecases/listNotes.ts';

/** The wire format. It stays in this module and maps to and from domain types. */
interface NoteResponse {
  readonly id: string;
  readonly title: string;
  readonly createdAt: string;
}

function toResponse(note: Note): NoteResponse {
  return { id: note.id, title: note.title, createdAt: note.createdAt.toISOString() };
}

function parseCreateRequest(body: unknown): { title: string } | undefined {
  if (typeof body === 'object' && body !== null && 'title' in body && typeof body.title === 'string') {
    return { title: body.title };
  }
  return undefined;
}

export function notesRoutes(deps: { createNote: CreateNote; listNotes: ListNotes; logger: Logger }): Route[] {
  return [
    {
      method: 'GET',
      path: '/notes',
      handle: async (_request, response) => {
        try {
          const notes = await deps.listNotes.run();
          sendJson(response, 200, notes.map(toResponse));
        } catch (error) {
          deps.logger.error('list notes failed', { error: String(error) });
          sendError(response, 500, 'notes_unavailable', 'The notes could not be loaded.');
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
          sendError(response, 400, 'invalid_request', 'Send a JSON object with a title.');
          return;
        }
        try {
          const result = await deps.createNote.run(body.title);
          if (result.ok) {
            sendJson(response, 201, toResponse(result.value));
          } else if (result.error === 'empty') {
            sendError(response, 422, 'title_empty', 'Enter a title.');
          } else {
            sendError(response, 422, 'title_too_long', `Use at most ${maxTitleLength} characters.`);
          }
        } catch (error) {
          deps.logger.error('create note failed', { error: String(error) });
          sendError(response, 500, 'note_not_saved', 'The note could not be saved.');
        }
      },
    },
  ];
}
