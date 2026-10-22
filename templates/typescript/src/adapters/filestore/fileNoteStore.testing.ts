import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { FileNoteStore } from './fileNoteStore.ts';

export async function temporaryNoteStore(): Promise<FileNoteStore> {
  const directory = await mkdtemp(join(tmpdir(), 'notes-'));
  return new FileNoteStore(join(directory, 'notes.json'));
}
