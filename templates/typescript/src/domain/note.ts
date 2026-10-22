import type { Result } from '../utilities/result.ts';

declare const noteTitleBrand: unique symbol;

export type NoteTitle = string & { readonly [noteTitleBrand]: true };

export const maxTitleLength = 200;

export type NoteTitleError = 'empty' | 'tooLong';

export interface Note {
  readonly id: string;
  readonly title: NoteTitle;
  readonly createdAt: Date;
}

function brokenTitleRule(trimmed: string): NoteTitleError | undefined {
  if (trimmed === '') return 'empty';
  // Array.from counts code points, so an emoji counts as one character, as in the Go template.
  if (Array.from(trimmed).length > maxTitleLength) return 'tooLong';
  return undefined;
}

export function isNoteTitle(value: string): value is NoteTitle {
  return value === value.trim() && brokenTitleRule(value) === undefined;
}

export function parseNoteTitle(raw: string): Result<NoteTitle, NoteTitleError> {
  const trimmed = raw.trim();
  const broken = brokenTitleRule(trimmed);
  if (broken !== undefined) return { ok: false, error: broken };
  if (!isNoteTitle(trimmed)) throw new Error('isNoteTitle and brokenTitleRule disagree.');
  return { ok: true, value: trimmed };
}
