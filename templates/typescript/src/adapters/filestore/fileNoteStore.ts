import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { parseNoteTitle, type Note } from '../../domain/note.ts';
import type { NoteStore } from '../../domain/ports.ts';

/** The stored form. Its field names are the stored format, so rename them only with a migration. */
interface NoteRecord {
  readonly id: string;
  readonly title: string;
  readonly createdAt: string;
}

/**
 * Stores notes as JSON in one file. Replace it with a database adapter as the
 * service grows; the domain and the slices do not change.
 */
export class FileNoteStore implements NoteStore {
  readonly #path: string;
  #queue: Promise<unknown> = Promise.resolve();

  constructor(path: string) {
    this.#path = path;
  }

  allNotes(): Promise<Note[]> {
    return this.#serialized(async () => (await this.#read()).map(toDomain));
  }

  save(note: Note): Promise<void> {
    return this.#serialized(async () => {
      const records = (await this.#read()).filter((record) => record.id !== note.id);
      await this.#write([...records, toRecord(note)]);
    });
  }

  /** Runs one operation at a time, so a read and a write never interleave. */
  #serialized<T>(work: () => Promise<T>): Promise<T> {
    const result = this.#queue.then(work, work);
    this.#queue = result.catch(() => undefined);
    return result;
  }

  async #read(): Promise<NoteRecord[]> {
    let text: string;
    try {
      text = await readFile(this.#path, 'utf8');
    } catch (error) {
      if (isNotFound(error)) return [];
      throw error;
    }
    return parseRecords(JSON.parse(text));
  }

  async #write(records: readonly NoteRecord[]): Promise<void> {
    await mkdir(dirname(this.#path), { recursive: true });
    const temporary = `${this.#path}.${process.pid}.tmp`;
    await writeFile(temporary, JSON.stringify(records));
    await rename(temporary, this.#path);
  }
}

function isNotFound(error: unknown): boolean {
  return typeof error === 'object' && error !== null && 'code' in error && error.code === 'ENOENT';
}

function parseRecords(value: unknown): NoteRecord[] {
  if (!Array.isArray(value)) throw new Error('The notes file does not hold a list.');
  return value.map(parseRecord);
}

function parseRecord(value: unknown): NoteRecord {
  if (
    typeof value === 'object' && value !== null &&
    'id' in value && typeof value.id === 'string' &&
    'title' in value && typeof value.title === 'string' &&
    'createdAt' in value && typeof value.createdAt === 'string'
  ) {
    return { id: value.id, title: value.title, createdAt: value.createdAt };
  }
  throw new Error('A stored note has an unexpected shape.');
}

function toDomain(record: NoteRecord): Note {
  const title = parseNoteTitle(record.title);
  if (!title.ok) throw new Error(`Stored note ${record.id} has an invalid title.`);
  return { id: record.id, title: title.value, createdAt: new Date(record.createdAt) };
}

function toRecord(note: Note): NoteRecord {
  return { id: note.id, title: note.title, createdAt: note.createdAt.toISOString() };
}
