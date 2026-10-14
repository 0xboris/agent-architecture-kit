import assert from 'node:assert/strict';
import { test } from 'node:test';
import { FakeClock, FakeNoteStore, SequentialIds, sampleNote } from '../../../testsupport/fakes.ts';
import { CreateNote } from './createNote.ts';
import { ListNotes } from './listNotes.ts';

test('a created note gets its id and time from the ports', async () => {
  const store = new FakeNoteStore();
  const now = new Date('2025-03-01T09:00:00Z');
  const createNote = new CreateNote({ store, clock: new FakeClock(now), ids: new SequentialIds() });

  const result = await createNote.run('Groceries');

  assert.ok(result.ok);
  assert.equal(result.value.id, 'id-001');
  assert.deepEqual(result.value.createdAt, now);
  assert.deepEqual(await store.allNotes(), [result.value]);
});

test('an invalid title is not stored', async () => {
  const store = new FakeNoteStore();
  const createNote = new CreateNote({ store, clock: new FakeClock(), ids: new SequentialIds() });

  assert.deepEqual(await createNote.run(''), { ok: false, error: 'empty' });
  assert.deepEqual(await store.allNotes(), []);
});

test('notes are listed newest first', async () => {
  const older = sampleNote(1, new Date('2025-01-01T00:00:00Z'));
  const newer = sampleNote(2, new Date('2025-01-02T00:00:00Z'));
  const listNotes = new ListNotes({ store: new FakeNoteStore([older, newer]) });

  assert.deepEqual(await listNotes.run(), [newer, older]);
});
