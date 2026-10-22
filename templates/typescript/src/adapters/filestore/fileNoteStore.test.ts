import assert from 'node:assert/strict';
import { copyFile, mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { parseNoteTitle } from '../../domain/note.ts';
import { sampleNote } from '../../testsupport/fakes.ts';
import { FileNoteStore } from './fileNoteStore.ts';
import { temporaryNoteStore } from './fileNoteStore.testing.ts';

test('a new store lists no notes', async () => {
  assert.deepEqual(await (await temporaryNoteStore()).allNotes(), []);
});

test('a saved note is listed', async () => {
  const store = await temporaryNoteStore();
  const note = sampleNote(1);
  await store.save(note);
  assert.deepEqual(await store.allNotes(), [note]);
});

test('saving the same id replaces the note', async () => {
  const store = await temporaryNoteStore();
  const original = sampleNote(1);
  const title = parseNoteTitle('Changed');
  assert.ok(title.ok);
  const replacement = { ...original, title: title.value };
  await store.save(original);
  await store.save(replacement);
  assert.deepEqual(await store.allNotes(), [replacement]);
});

test('a file written by version 1 still loads', async () => {
  const path = join(await mkdtemp(join(tmpdir(), 'notes-')), 'notes.json');
  await copyFile(new URL('./testdata/notes-v1.json', import.meta.url), path);
  assert.deepEqual(await new FileNoteStore(path).allNotes(), [sampleNote(1)]);
});
