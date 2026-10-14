import type { Note } from './note.ts';

/**
 * Stores notes between runs. The filestore adapter implements it, testsupport
 * fakes it, and noteStoreContract checks that both behave the same.
 */
export interface NoteStore {
  allNotes(): Promise<Note[]>;
  save(note: Note): Promise<void>;
}

export interface Clock {
  now(): Date;
}

export interface IdGenerator {
  newId(): string;
}
