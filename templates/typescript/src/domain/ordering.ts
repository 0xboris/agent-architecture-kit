import type { Note } from './note.ts';

/** The order in which notes appear everywhere: newest first, and by id when two notes share a creation time. */
export function newestFirst(notes: readonly Note[]): Note[] {
  return [...notes].sort(
    (a, b) => b.createdAt.getTime() - a.createdAt.getTime() || a.id.localeCompare(b.id, 'en'),
  );
}
