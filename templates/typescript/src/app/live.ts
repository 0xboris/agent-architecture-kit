import { join } from 'node:path';
import { FileNoteStore } from '../adapters/filestore/fileNoteStore.ts';
import { ConsoleLogger, RandomIds, SystemClock } from '../adapters/platform/platform.ts';
import type { Config } from './config.ts';
import type { Dependencies } from './container.ts';

export function liveDependencies(config: Config): Dependencies {
  return {
    noteStore: new FileNoteStore(join(config.dataDir, 'notes.json')),
    clock: new SystemClock(),
    ids: new RandomIds(),
    logger: new ConsoleLogger(),
  };
}
