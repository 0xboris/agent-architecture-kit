import type { Note } from './note.ts';

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
