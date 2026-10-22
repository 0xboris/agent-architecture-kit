import assert from 'node:assert/strict';
import { test } from 'node:test';
import { isNoteTitle, maxTitleLength, parseNoteTitle } from './note.ts';

test('a title is trimmed', () => {
  assert.deepEqual(parseNoteTitle('  Groceries  '), { ok: true, value: 'Groceries' });
});

test('an empty title is rejected', () => {
  assert.deepEqual(parseNoteTitle('   '), { ok: false, error: 'empty' });
});

test('a title longer than the limit is rejected', () => {
  assert.deepEqual(parseNoteTitle('a'.repeat(maxTitleLength + 1)), { ok: false, error: 'tooLong' });
});

test('only a trimmed, non-empty title within the limit counts as a note title', () => {
  assert.equal(isNoteTitle('Groceries'), true);
  assert.equal(isNoteTitle(' Groceries'), false);
  assert.equal(isNoteTitle(''), false);
  assert.equal(isNoteTitle('a'.repeat(maxTitleLength + 1)), false);
});
