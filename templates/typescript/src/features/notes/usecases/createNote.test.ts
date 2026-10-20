import assert from 'node:assert/strict';
import { mock, test } from 'node:test';
import type { NoteStore } from '../../../domain/ports.ts';
import { FakeClock, SequentialIds, sampleNote } from '../../../testsupport/fakes.ts';
import { CreateNote } from './createNote.ts';
import { ListNotes } from './listNotes.ts';

test('a created note gets its id and time from the ports and is saved', async () => {
  const save = mock.fn<NoteStore['save']>(() => Promise.resolve());
  const store: NoteStore = { allNotes: () => Promise.resolve([]), save };
  const now = new Date('2025-03-01T09:00:00Z');
  const createNote = new CreateNote({ store, clock: new FakeClock(now), ids: new SequentialIds() });

  const result = await createNote.run('Groceries');

  assert.ok(result.ok);
  assert.equal(result.value.id, 'id-001');
  assert.deepEqual(result.value.createdAt, now);
  assert.deepEqual(save.mock.calls.map((call) => call.arguments), [[result.value]]);
});

test('an invalid title is not saved', async () => {
  const save = mock.fn<NoteStore['save']>(() => Promise.resolve());
  const store: NoteStore = { allNotes: () => Promise.resolve([]), save };
  const createNote = new CreateNote({ store, clock: new FakeClock(), ids: new SequentialIds() });

  assert.deepEqual(await createNote.run(''), { ok: false, error: 'empty' });
  assert.equal(save.mock.callCount(), 0);
});

test('a failed save reaches the caller', async () => {
  const store: NoteStore = {
    allNotes: () => Promise.resolve([]),
    save: () => Promise.reject(new Error('offline')),
  };
  const createNote = new CreateNote({ store, clock: new FakeClock(), ids: new SequentialIds() });

  await assert.rejects(createNote.run('Groceries'), /offline/);
});

test('notes are listed newest first', async () => {
  const older = sampleNote(1, new Date('2025-01-01T00:00:00Z'));
  const newer = sampleNote(2, new Date('2025-01-02T00:00:00Z'));
  const store: NoteStore = { allNotes: () => Promise.resolve([older, newer]), save: () => Promise.resolve() };

  assert.deepEqual(await new ListNotes({ store }).run(), [newer, older]);
});
