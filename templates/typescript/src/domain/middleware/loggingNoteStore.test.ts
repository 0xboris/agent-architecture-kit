import assert from 'node:assert/strict';
import { test } from 'node:test';
import { FakeNoteStore, RecordingLogger, sampleNote } from '../../testsupport/fakes.ts';
import { LoggingNoteStore } from './loggingNoteStore.ts';

test('saving through the middleware logs and stores', async () => {
  const store = new FakeNoteStore();
  const logger = new RecordingLogger();
  const note = sampleNote(1);

  await new LoggingNoteStore(store, logger).save(note);

  assert.deepEqual(await store.allNotes(), [note]);
  assert.deepEqual(logger.messages, ['note saved']);
});

test('a failed save is not logged', async () => {
  const store = new FakeNoteStore();
  store.failNextCall(new Error('offline'));
  const logger = new RecordingLogger();

  await assert.rejects(new LoggingNoteStore(store, logger).save(sampleNote(1)), /offline/);
  assert.deepEqual(logger.messages, []);
});
