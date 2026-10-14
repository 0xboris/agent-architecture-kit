import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { parseNoteTitle } from '../domain/note.ts';
import type { NoteStore } from '../domain/ports.ts';
import { sampleNote } from './fakes.ts';

/**
 * The behavior that every NoteStore must have. The fake runs it in
 * fakes.test.ts and the file store in its own tests, so the fake cannot drift
 * from the real store.
 */
export function noteStoreContract(name: string, makeStore: () => NoteStore | Promise<NoteStore>): void {
  describe(`${name} meets the NoteStore contract`, () => {
    test('an empty store lists no notes', async () => {
      assert.deepEqual(await (await makeStore()).allNotes(), []);
    });

    test('a saved note is listed', async () => {
      const store = await makeStore();
      const note = sampleNote(1);
      await store.save(note);
      assert.deepEqual(await store.allNotes(), [note]);
    });

    test('saving the same id replaces the note', async () => {
      const store = await makeStore();
      const original = sampleNote(1);
      const title = parseNoteTitle('Changed');
      assert.ok(title.ok);
      const replacement = { ...original, title: title.value };
      await store.save(original);
      await store.save(replacement);
      assert.deepEqual(await store.allNotes(), [replacement]);
    });
  });
}
