import assert from 'node:assert/strict';
import { test } from 'node:test';
import { temporaryNoteStore } from '../adapters/filestore/fileNoteStore.testing.ts';
import { FakeClock, RecordingLogger, SequentialIds } from '../testsupport/fakes.ts';
import { startTestServer } from '../testsupport/http.ts';
import { createApp } from './container.ts';

test('the notes slice stores through the logging middleware', async (t) => {
  const store = await temporaryNoteStore(t);
  const logger = new RecordingLogger();
  const app = createApp({ noteStore: store, clock: new FakeClock(), ids: new SequentialIds(), logger });
  const server = await startTestServer(app.handle);
  try {
    const response = await fetch(`${server.url}/notes`, { method: 'POST', body: JSON.stringify({ title: 'Groceries' }) });
    assert.equal(response.status, 201);
  } finally {
    await server.close();
  }
  assert.equal((await store.allNotes()).length, 1);
  assert.deepEqual(logger.messages, ['note saved']);
});
