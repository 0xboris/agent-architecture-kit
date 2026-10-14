import type { Result } from '../utilities/result.ts';

declare const noteTitleBrand: unique symbol;

/** A title that follows the title rules. Only parseNoteTitle creates one. */
export type NoteTitle = string & { readonly [noteTitleBrand]: true };

export const maxTitleLength = 200;

export type NoteTitleError = 'empty' | 'tooLong';

export interface Note {
  readonly id: string;
  readonly title: NoteTitle;
  readonly createdAt: Date;
}

export function parseNoteTitle(raw: string): Result<NoteTitle, NoteTitleError> {
  const trimmed = raw.trim();
  if (trimmed === '') return { ok: false, error: 'empty' };
  if ([...trimmed].length > maxTitleLength) return { ok: false, error: 'tooLong' };
  return { ok: true, value: trimmed as NoteTitle };
}
