import assert from 'node:assert/strict';
import { test } from 'node:test';
import { FakeClock, FakeNoteStore, RecordingLogger, SequentialIds } from '../testsupport/fakes.ts';
import { startTestServer } from '../testsupport/http.ts';
import { createApp } from './container.ts';

// Composition tests check the wiring in createApp: which middleware each slice
// receives. Unit tests of a slice use fakes and never see the wiring.
test('the notes slice stores through the logging middleware', async () => {
  const store = new FakeNoteStore();
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
