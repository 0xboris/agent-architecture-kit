import assert from 'node:assert/strict';
import { test } from 'node:test';
import { sampleNote } from '../testsupport/fakes.ts';
import { newestFirst } from './ordering.ts';

test('the newest note comes first', () => {
  const older = sampleNote(1, new Date('2025-01-01T00:00:00Z'));
  const newer = sampleNote(2, new Date('2025-01-02T00:00:00Z'));
  assert.deepEqual(newestFirst([older, newer]), [newer, older]);
});

test('notes with the same time are ordered by id', () => {
  const first = sampleNote(1);
  const second = sampleNote(2);
  assert.deepEqual(newestFirst([second, first]), [first, second]);
});
