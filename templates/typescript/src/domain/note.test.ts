import assert from 'node:assert/strict';
import { test } from 'node:test';
import { maxTitleLength, parseNoteTitle } from './note.ts';

test('a title is trimmed', () => {
  assert.deepEqual(parseNoteTitle('  Groceries  '), { ok: true, value: 'Groceries' });
});

test('an empty title is rejected', () => {
  assert.deepEqual(parseNoteTitle('   '), { ok: false, error: 'empty' });
});

test('a title longer than the limit is rejected', () => {
  assert.deepEqual(parseNoteTitle('a'.repeat(maxTitleLength + 1)), { ok: false, error: 'tooLong' });
});
