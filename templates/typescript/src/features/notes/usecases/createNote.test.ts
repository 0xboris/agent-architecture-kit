import assert from 'node:assert/strict';
import { test } from 'node:test';
import { temporaryNoteStore } from '../../../adapters/filestore/fileNoteStore.testing.ts';
import { FakeClock, SequentialIds, failingNoteStore } from '../../../testsupport/fakes.ts';
import { createNote } from './createNote.ts';

test('a created note gets its id and time from the ports and is stored', async (t) => {
  const store = await temporaryNoteStore(t);
  const now = new Date('2025-03-01T09:00:00Z');

  const result = await createNote({ store, clock: new FakeClock(now), ids: new SequentialIds() }, 'Groceries');

  assert.ok(result.ok);
  assert.equal(result.value.id, 'id-001');
  assert.deepEqual(result.value.createdAt, now);
  assert.deepEqual(await store.allNotes(), [result.value]);
});

test('an invalid title is not stored', async (t) => {
  const store = await temporaryNoteStore(t);

  const result = await createNote({ store, clock: new FakeClock(), ids: new SequentialIds() }, '');

  assert.deepEqual(result, { ok: false, error: 'empty' });
  assert.deepEqual(await store.allNotes(), []);
});

test('a failed save reaches the caller', async () => {
  const store = failingNoteStore(new Error('offline'));

  await assert.rejects(createNote({ store, clock: new FakeClock(), ids: new SequentialIds() }, 'Groceries'), /offline/);
});
