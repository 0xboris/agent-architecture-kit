import type { Note } from './note.ts';

/** Stores notes between runs. The filestore adapter implements it. */
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
