import { parseNoteTitle, type Note } from '../domain/note.ts';
import type { Clock, IdGenerator, NoteStore } from '../domain/ports.ts';
import type { Logger } from '../utilities/logger.ts';

/**
 * The shared fake for NoteStore. noteStoreContract checks that it behaves like
 * the real store. Use failNextCall to test error handling.
 */
export class FakeNoteStore implements NoteStore {
  readonly #notes = new Map<string, Note>();
  #nextError: Error | undefined;

  constructor(notes: readonly Note[] = []) {
    for (const note of notes) this.#notes.set(note.id, note);
  }

  failNextCall(error: Error): void {
    this.#nextError = error;
  }

  async allNotes(): Promise<Note[]> {
    this.#throwPendingError();
    return [...this.#notes.values()];
  }

  async save(note: Note): Promise<void> {
    this.#throwPendingError();
    this.#notes.set(note.id, note);
  }

  #throwPendingError(): void {
    const error = this.#nextError;
    this.#nextError = undefined;
    if (error !== undefined) throw error;
  }
}

/** A clock that starts at a fixed time and moves only when a test calls advance. */
export class FakeClock implements Clock {
  #now: Date;

  constructor(start: Date = new Date('2025-01-01T00:00:00Z')) {
    this.#now = start;
  }

  now(): Date {
    return this.#now;
  }

  advance(milliseconds: number): void {
    this.#now = new Date(this.#now.getTime() + milliseconds);
  }
}

/** Returns id-001, id-002, and so on. */
export class SequentialIds implements IdGenerator {
  #next = 0;

  newId(): string {
    this.#next += 1;
    return `id-${String(this.#next).padStart(3, '0')}`;
  }
}

export class RecordingLogger implements Logger {
  readonly messages: string[] = [];

  info(message: string): void {
    this.messages.push(message);
  }

  error(message: string): void {
    this.messages.push(message);
  }
}

export function sampleNote(number: number, createdAt: Date = new Date('2025-01-01T00:00:00Z')): Note {
  const title = parseNoteTitle(`Note ${number}`);
  if (!title.ok) throw new Error('The sample title is invalid.');
  return { id: `id-${String(number).padStart(3, '0')}`, title: title.value, createdAt };
}
