import assert from 'node:assert/strict';
import { test } from 'node:test';
import { temporaryNoteStore } from '../../../adapters/filestore/fileNoteStore.testing.ts';
import { sampleNote } from '../../../testsupport/fakes.ts';
import { listNotes } from './listNotes.ts';

test('notes are listed newest first', async (t) => {
  const store = await temporaryNoteStore(t);
  const older = sampleNote(1, new Date('2025-01-01T00:00:00Z'));
  const newer = sampleNote(2, new Date('2025-01-02T00:00:00Z'));
  await store.save(older);
  await store.save(newer);

  assert.deepEqual(await listNotes({ store }), [newer, older]);
});
