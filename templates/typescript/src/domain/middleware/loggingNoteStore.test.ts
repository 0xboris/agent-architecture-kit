import assert from 'node:assert/strict';
import { test } from 'node:test';
import { temporaryNoteStore } from '../../adapters/filestore/fileNoteStore.testing.ts';
import { RecordingLogger, failingNoteStore, sampleNote } from '../../testsupport/fakes.ts';
import { LoggingNoteStore } from './loggingNoteStore.ts';

test('a note saved through the middleware is stored and logged', async (t) => {
  const store = await temporaryNoteStore(t);
  const logger = new RecordingLogger();
  const note = sampleNote(1);

  await new LoggingNoteStore(store, logger).save(note);

  assert.deepEqual(await store.allNotes(), [note]);
  assert.deepEqual(logger.messages, ['note saved']);
});

test('a failed save is not logged', async () => {
  const logger = new RecordingLogger();

  await assert.rejects(new LoggingNoteStore(failingNoteStore(new Error('offline')), logger).save(sampleNote(1)), /offline/);
  assert.deepEqual(logger.messages, []);
});
