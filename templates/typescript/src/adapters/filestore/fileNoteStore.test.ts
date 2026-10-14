import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { noteStoreContract } from '../../testsupport/noteStoreContract.ts';
import { FileNoteStore } from './fileNoteStore.ts';

noteStoreContract('FileNoteStore', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'notes-'));
  return new FileNoteStore(join(directory, 'notes.json'));
});
