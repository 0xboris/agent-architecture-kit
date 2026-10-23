import assert from 'node:assert/strict';
import { copyFile } from 'node:fs/promises';
import { join } from 'node:path';
import { test } from 'node:test';
import { parseNoteTitle } from '../../domain/note.ts';
import { sampleNote } from '../../testsupport/fakes.ts';
import { FileNoteStore } from './fileNoteStore.ts';
import { temporaryDirectory, temporaryNoteStore } from './fileNoteStore.testing.ts';

test('a new store lists no notes', async (t) => {
  assert.deepEqual(await (await temporaryNoteStore(t)).allNotes(), []);
});

test('a saved note is listed', async (t) => {
  const store = await temporaryNoteStore(t);
  const note = sampleNote(1);
  await store.save(note);
  assert.deepEqual(await store.allNotes(), [note]);
});

test('saving the same id replaces the note', async (t) => {
  const store = await temporaryNoteStore(t);
  const original = sampleNote(1);
  const title = parseNoteTitle('Changed');
  assert.ok(title.ok);
  const replacement = { ...original, title: title.value };
  await store.save(original);
  await store.save(replacement);
  assert.deepEqual(await store.allNotes(), [replacement]);
});

test('a file written by version 1 still loads', async (t) => {
  const path = join(await temporaryDirectory(t), 'notes.json');
  await copyFile(new URL('./testdata/notes-v1.json', import.meta.url), path);
  assert.deepEqual(await new FileNoteStore(path).allNotes(), [sampleNote(1)]);
});
