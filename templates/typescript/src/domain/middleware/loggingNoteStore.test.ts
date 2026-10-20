import assert from 'node:assert/strict';
import { mock, test } from 'node:test';
import { RecordingLogger, sampleNote } from '../../testsupport/fakes.ts';
import type { NoteStore } from '../ports.ts';
import { LoggingNoteStore } from './loggingNoteStore.ts';

test('saving through the middleware saves and logs', async () => {
  const save = mock.fn<NoteStore['save']>(() => Promise.resolve());
  const logger = new RecordingLogger();
  const note = sampleNote(1);

  await new LoggingNoteStore({ allNotes: () => Promise.resolve([]), save }, logger).save(note);

  assert.deepEqual(save.mock.calls.map((call) => call.arguments), [[note]]);
  assert.deepEqual(logger.messages, ['note saved']);
});

test('a failed save is not logged', async () => {
  const store: NoteStore = {
    allNotes: () => Promise.resolve([]),
    save: () => Promise.reject(new Error('offline')),
  };
  const logger = new RecordingLogger();

  await assert.rejects(new LoggingNoteStore(store, logger).save(sampleNote(1)), /offline/);
  assert.deepEqual(logger.messages, []);
});
