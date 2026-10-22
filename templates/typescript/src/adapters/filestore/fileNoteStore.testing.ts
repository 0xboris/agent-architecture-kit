import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import type { TestContext } from 'node:test';
import { FileNoteStore } from './fileNoteStore.ts';

export async function temporaryDirectory(t: TestContext): Promise<string> {
  const directory = await mkdtemp(join(tmpdir(), 'notes-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  return directory;
}

export async function temporaryNoteStore(t: TestContext): Promise<FileNoteStore> {
  return new FileNoteStore(join(await temporaryDirectory(t), 'notes.json'));
}
