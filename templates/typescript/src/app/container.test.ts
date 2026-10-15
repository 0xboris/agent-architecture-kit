import assert from 'node:assert/strict';
import { mock, test } from 'node:test';
import type { NoteStore } from '../domain/ports.ts';
import { FakeClock, RecordingLogger, SequentialIds } from '../testsupport/fakes.ts';
import { startTestServer } from '../testsupport/http.ts';
import { createApp } from './container.ts';

// Composition tests check the wiring in createApp: which middleware each slice
// receives. Unit tests of a slice build their use cases directly and never see the wiring.
test('the notes slice stores through the logging middleware', async () => {
  const save = mock.fn<NoteStore['save']>(async () => {});
  const logger = new RecordingLogger();
  const app = createApp({
    noteStore: { allNotes: async () => [], save },
    clock: new FakeClock(),
    ids: new SequentialIds(),
    logger,
  });
  const server = await startTestServer(app.handle);
  try {
    const response = await fetch(`${server.url}/notes`, { method: 'POST', body: JSON.stringify({ title: 'Groceries' }) });
    assert.equal(response.status, 201);
  } finally {
    await server.close();
  }
  assert.equal(save.mock.callCount(), 1);
  assert.deepEqual(logger.messages, ['note saved']);
});
