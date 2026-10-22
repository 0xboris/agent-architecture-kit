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

export function isNoteTitle(value: string): value is NoteTitle {
  // Array.from counts code points, so an emoji counts as one character, as in the Go template.
  return value !== '' && value === value.trim() && Array.from(value).length <= maxTitleLength;
}

export function parseNoteTitle(raw: string): Result<NoteTitle, NoteTitleError> {
  const trimmed = raw.trim();
  if (trimmed === '') return { ok: false, error: 'empty' };
  if (!isNoteTitle(trimmed)) return { ok: false, error: 'tooLong' };
  return { ok: true, value: trimmed };
}
