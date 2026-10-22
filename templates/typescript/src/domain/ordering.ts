import type { Note } from './note.ts';

/** Sorts notes newest first, and by id when two notes share a creation time. Every list of notes uses this order. */
export function newestFirst(notes: readonly Note[]): Note[] {
  return [...notes].sort(
    (a, b) => b.createdAt.getTime() - a.createdAt.getTime() || a.id.localeCompare(b.id, 'en'),
  );
}
