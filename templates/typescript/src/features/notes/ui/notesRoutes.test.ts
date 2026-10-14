import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createRouter } from '../../../sharedui/http.ts';
import { FakeClock, FakeNoteStore, RecordingLogger, SequentialIds } from '../../../testsupport/fakes.ts';
import { startTestServer } from '../../../testsupport/http.ts';
import { CreateNote } from '../usecases/createNote.ts';
import { ListNotes } from '../usecases/listNotes.ts';
import { notesRoutes } from './notesRoutes.ts';

async function withServer(store: FakeNoteStore, run: (url: string) => Promise<void>): Promise<void> {
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

test('posting a note returns created', async () => {
  await withServer(new FakeNoteStore(), async (url) => {
    const response = await fetch(`${url}/notes`, { method: 'POST', body: JSON.stringify({ title: 'Groceries' }) });
    assert.equal(response.status, 201);
    assert.equal((await response.json()).title, 'Groceries');
  });
});

test('posting an empty title returns unprocessable', async () => {
  await withServer(new FakeNoteStore(), async (url) => {
    const response = await fetch(`${url}/notes`, { method: 'POST', body: JSON.stringify({ title: ' ' }) });
    assert.equal(response.status, 422);
    assert.equal((await response.json()).code, 'title_empty');
  });
});

test('a failed load returns a server error', async () => {
  const store = new FakeNoteStore();
  store.failNextCall(new Error('offline'));
  await withServer(store, async (url) => {
    const response = await fetch(`${url}/notes`);
    assert.equal(response.status, 500);
  });
});
