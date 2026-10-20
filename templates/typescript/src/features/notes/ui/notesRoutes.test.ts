import assert from 'node:assert/strict';
import { test } from 'node:test';
import type { NoteStore } from '../../../domain/ports.ts';
import { createRouter } from '../../../sharedui/http.ts';
import { FakeClock, RecordingLogger, SequentialIds, sampleNote } from '../../../testsupport/fakes.ts';
import { startTestServer } from '../../../testsupport/http.ts';
import { CreateNote } from '../usecases/createNote.ts';
import { ListNotes } from '../usecases/listNotes.ts';
import { notesRoutes } from './notesRoutes.ts';

async function withServer(store: NoteStore, run: (url: string) => Promise<void>): Promise<void> {
  const routes = notesRoutes({
    createNote: new CreateNote({ store, clock: new FakeClock(), ids: new SequentialIds() }),
    listNotes: new ListNotes({ store }),
    logger: new RecordingLogger(),
  });
  const server = await startTestServer(createRouter(routes, () => undefined));
  try {
    await run(server.url);
  } finally {
    await server.close();
  }
}

const emptyStore: NoteStore = { allNotes: () => Promise.resolve([]), save: () => Promise.resolve() };

test('listing notes returns them', async () => {
  const store: NoteStore = { allNotes: () => Promise.resolve([sampleNote(1)]), save: () => Promise.resolve() };
  await withServer(store, async (url) => {
    const response = await fetch(`${url}/notes`);
    assert.equal(response.status, 200);
    const body = (await response.json()) as { title: string }[];
    assert.deepEqual(body.map((note) => note.title), ['Note 1']);
  });
});

test('posting a note returns created', async () => {
  await withServer(emptyStore, async (url) => {
    const response = await fetch(`${url}/notes`, { method: 'POST', body: JSON.stringify({ title: 'Groceries' }) });
    assert.equal(response.status, 201);
    assert.equal(((await response.json()) as { title: string }).title, 'Groceries');
  });
});

test('posting an empty title returns unprocessable', async () => {
  await withServer(emptyStore, async (url) => {
    const response = await fetch(`${url}/notes`, { method: 'POST', body: JSON.stringify({ title: ' ' }) });
    assert.equal(response.status, 422);
    assert.equal(((await response.json()) as { code: string }).code, 'title_empty');
  });
});

test('a failed load returns a server error', async () => {
  const store: NoteStore = {
    allNotes: () => Promise.reject(new Error('offline')),
    save: () => Promise.resolve(),
  };
  await withServer(store, async (url) => {
    const response = await fetch(`${url}/notes`);
    assert.equal(response.status, 500);
  });
});
