import type { Result } from '../utilities/result.ts';

export type NoteTitle = string & { readonly __brand: 'NoteTitle' };

export const maxTitleLength = 200;

export type NoteTitleError = 'empty' | 'tooLong';

export interface Note {
  readonly id: string;
  readonly title: NoteTitle;
  readonly createdAt: Date;
}

function brokenTitleRule(trimmed: string): NoteTitleError | undefined {
  if (trimmed === '') return 'empty';
  // Count code points, as the Go template does. string.length counts UTF-16 units, so most emoji would count twice.
  if (Array.from(trimmed).length > maxTitleLength) return 'tooLong';
  return undefined;
}

export function isNoteTitle(value: string): value is NoteTitle {
  return value === value.trim() && brokenTitleRule(value) === undefined;
}

export function parseNoteTitle(raw: string): Result<NoteTitle, NoteTitleError> {
  const trimmed = raw.trim();
  if (isNoteTitle(trimmed)) return { ok: true, value: trimmed };
  const broken = brokenTitleRule(trimmed);
  if (broken === undefined) throw new Error('isNoteTitle rejected a title that breaks no rule.');
  return { ok: false, error: broken };
}
