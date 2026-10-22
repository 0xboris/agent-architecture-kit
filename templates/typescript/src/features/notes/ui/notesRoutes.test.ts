import assert from 'node:assert/strict';
import { test } from 'node:test';
import { temporaryNoteStore } from '../../../adapters/filestore/fileNoteStore.testing.ts';
import type { NoteStore } from '../../../domain/ports.ts';
import { createRouter } from '../../../sharedui/http.ts';
import { FakeClock, RecordingLogger, SequentialIds, failingNoteStore, sampleNote } from '../../../testsupport/fakes.ts';
import { startTestServer } from '../../../testsupport/http.ts';
import { createNote } from '../usecases/createNote.ts';
import { listNotes } from '../usecases/listNotes.ts';
import { notesRoutes } from './notesRoutes.ts';

async function withServer(store: NoteStore, run: (url: string) => Promise<void>): Promise<void> {
  const ports = { store, clock: new FakeClock(), ids: new SequentialIds() };
  const routes = notesRoutes({
    createNote: (rawTitle) => createNote(ports, rawTitle),
    listNotes: () => listNotes({ store }),
    logger: new RecordingLogger(),
  });
  const server = await startTestServer(createRouter(routes, () => undefined));
  try {
    await run(server.url);
  } finally {
    await server.close();
  }
}

test('listing notes returns them', async () => {
  const store = await temporaryNoteStore();
  await store.save(sampleNote(1));
  await withServer(store, async (url) => {
    const response = await fetch(`${url}/notes`);
    assert.equal(response.status, 200);
    const body = (await response.json()) as { title: string }[];
    assert.deepEqual(body.map((note) => note.title), ['Note 1']);
  });
});

test('a posted note is created and listed', async () => {
  await withServer(await temporaryNoteStore(), async (url) => {
    const created = await fetch(`${url}/notes`, { method: 'POST', body: JSON.stringify({ title: 'Groceries' }) });
    assert.equal(created.status, 201);
    assert.equal(((await created.json()) as { title: string }).title, 'Groceries');
    const listed = (await (await fetch(`${url}/notes`)).json()) as { title: string }[];
    assert.deepEqual(listed.map((note) => note.title), ['Groceries']);
  });
});

test('posting an empty title returns unprocessable', async () => {
  await withServer(await temporaryNoteStore(), async (url) => {
    const response = await fetch(`${url}/notes`, { method: 'POST', body: JSON.stringify({ title: ' ' }) });
    assert.equal(response.status, 422);
    assert.equal(((await response.json()) as { code: string }).code, 'title_empty');
  });
});

test('a failed load returns a server error', async () => {
  await withServer(failingNoteStore(new Error('offline')), async (url) => {
    const response = await fetch(`${url}/notes`);
    assert.equal(response.status, 500);
  });
});
