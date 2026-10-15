import assert from 'node:assert/strict';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { parseNoteTitle } from '../../domain/note.ts';
import { sampleNote } from '../../testsupport/fakes.ts';
import { FileNoteStore } from './fileNoteStore.ts';

// The adapter is tested against the real file system, in a temporary directory.
async function newStore(): Promise<FileNoteStore> {
  const directory = await mkdtemp(join(tmpdir(), 'notes-'));
  return new FileNoteStore(join(directory, 'notes.json'));
}

test('a new store lists no notes', async () => {
  assert.deepEqual(await (await newStore()).allNotes(), []);
});

test('a saved note is listed', async () => {
  const store = await newStore();
  const note = sampleNote(1);
  await store.save(note);
  assert.deepEqual(await store.allNotes(), [note]);
});

test('saving the same id replaces the note', async () => {
  const store = await newStore();
  const original = sampleNote(1);
  const title = parseNoteTitle('Changed');
  assert.ok(title.ok);
  const replacement = { ...original, title: title.value };
  await store.save(original);
  await store.save(replacement);
  assert.deepEqual(await store.allNotes(), [replacement]);
});
